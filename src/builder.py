import json

# Extensions
import markdown

class Builder:

  OUTPUT_DIR = 'bin' # where to build to
  DATA_DIR = 'data' # where our data files are
  DATABASE_FILE = "{0}/games.json".format(DATA_DIR)
  STATIC_PAGES_DIR = "{0}/static_pages".format(DATA_DIR)
  IMAGES_DIR = "{0}/images".format(DATA_DIR)
  GAMES_DIR = "{0}/games".format(DATA_DIR)
  GUIDES_DIR = "{0}/guides".format(DATA_DIR)

  TEMPLATE_DIRECTORY = 'templates'
  # We copy the template dir. But not these items.
  TEMPLATE_EXCLUSIONS = ['snippets']

  INDEX_PAGE = 'index.html' # the home index page; this is also the layout.
  NAVBAR_LINKS_PLACEHOLDER = '<!-- DG navbar links -->' # Where the navbar list of pages goes
  # Snippets where we put in real data (eg. game page URLs)
  NAVBAR_LINK_SNIPPET = "{0}/snippets/navbar_link.html".format(TEMPLATE_DIRECTORY)
  JUMBOTRON_SNIPPET = "{0}/snippets/jumbotron.html".format(TEMPLATE_DIRECTORY)
  SCREENSHOTS_SNIPPET = "{0}/snippets/screenshots.html".format(TEMPLATE_DIRECTORY)
  CONTENT_PLACEHOLDER = '<!-- DG content -->' # Where in the template we fill in the page content
  GAME_PAGE_TEMPLATE = "{0}/game.html".format(TEMPLATE_DIRECTORY)

  GOOGLE_PLAY_PATH = 'https://play.google.com/store/apps/details?id=' # URL for Google Play

  # When scaling images, scale down to this width/height (whatever's smaller)
  # The image width (if a landscape image) is guaranteed to be 250px or less
  # The image height (if a portrait image) is guaranteed to be 250px or less
  MAX_SCREENSHOT_SIZE = 250

  def build(self):
    start = Time.new
    self.verify_files_exist()
    self.__load_data()
    self.generate_site()
    stop = Time.new
    print("Done in #{stop - start} seconds.")
  end

  def __load_data(self):
    self.games = JSON.parse(File.read(DATABASE_FILE))['games'].sort! {
      # sort by publication date, reverse chronologically
      |x, y| Time.parse(y['published']) <=> Time.parse(x['published'])
    }
    raise 'JSON structure changed; where is the top-level "games" list?' if self.games.None?
  end

  def __verify_files_exist(self):
    raise "#{DATABASE_FILE} not found" unless File.exist?(DATABASE_FILE)
    raise "#{TEMPLATE_DIRECTORY} directory not found" unless Dir.exist?(TEMPLATE_DIRECTORY)
  end

  def __generate_site(self):
    # Copy over CSS, fonts, JS, and the index page, plus site-wide images, etc.
    FileUtils.cp_r "#{TEMPLATE_DIRECTORY}/.", OUTPUT_DIR
    for exclusion in TEMPLATE_EXCLUSIONS:
      FileUtils.rm_rf exclusion
    end
    FileUtils.cp_r GAMES_DIR, OUTPUT_DIR
    FileUtils.cp_r GUIDES_DIR, OUTPUT_DIR

    generate_master_page
    generate_static_pages
    generate_front_page_game_entries
    generate_game_pages
  end

  def __generate_game_pages(self):
    for g in self.games:
      html = File.read("#{GAME_PAGE_TEMPLATE}")
      html = html
        .replace('@name', g['name'])
        .replace('@blurb', g['blurb'])
        .replace('@version', g['version'] || '1.0.0')

      # Start adding per-platform HTML
      # For HTML5 and Flash, add in-page game playing
      html = get_inpage_platforms_html(g, html)
      html = get_downloadable_platforms_html(g, html)
      html = get_mobile_links(g, html)
      html = get_screenshots(g, html)
      html = get_educators_guide(g, html)
      final_html = self.master_page_html.sub(CONTENT_PLACEHOLDER, html).replace('@title', g['name'])
      filename = url_for_game(g)
      File.open("#{OUTPUT_DIR}/#{filename}", 'w') { |f| f.write(final_html) }
    end
  end
 
  def __get_educators_guide(self, g, html)
    link = ''
    if !g['educators_guide'].None?
      link = "<br /><a href='guides/#{g['educators_guide']}'><img src='images/educators_guide.svg' width='32' height='32' /> Parents/Educators Guide</a>";
    end
    html = html.replace('@educators_guide', link)
    return html
  end

  # Replace @screenshots with screenshots
  def __get_screenshots(self, g, html)
    if !g['screenshots'].None?
      template = File.read(SCREENSHOTS_SNIPPET)
      name = url_for_game(g).sub('.html', '')
      ss_html = ''
      for s in g['screenshots']:
        url = "images/#{name}/#{s}"
        native_size = FastImage.size("data/#{url}") # [w, h]
        raise "Can't get native size of images/#{name}/#{s}" if native_size.None?
        # Scale to 250px. Unless the image is already smaller. Then don't scale.
        scale = [1.0 * MAX_SCREENSHOT_SIZE / native_size[0],  1.0 * MAX_SCREENSHOT_SIZE / native_size[1], 1].min
        scale_w = (scale * native_size[0]).to_i
        scale_h = (scale * native_size[1]).to_i
        ss_html = "#{ss_html}<img src='#{url}' width='#{scale_w}' height='#{scale_h}' data-jslghtbx='#{url}' class='screenshot' />"
      end
      template = template.replace('@screenshots', ss_html)
      html = html.replace('@screenshots', template)
    else
      html = html.replace('@screenshots', '')
    end
    return html
  end

  # Modifies "html": replaces @mobile with mobile links
  def __get_mobile_links(self, g, html)
    links_html = ''
    mobile_data = platform_data(g, ['android']) #TODO: iOS
    if !mobile_data.empty?
      mobile_data.each do |platform, data|
        link_target = "#{GOOGLE_PLAY_PATH}#{data}"
        links_html += "<a href='#{link_target}'><img src='images/google-play-badge.png' /></a>"
      end
      html = html.replace('@mobile', links_html)
    else
      html = html.replace('@mobile', '')
    end
    return html
  end

  # Modifies "html": replaces @downloads with download links
  def __get_downloadable_platforms_html(self, g, html)
    downloadable_data = platform_data(g, ['windows', 'linux', 'mac'])
    template = File.read("#{TEMPLATE_DIRECTORY}/snippets/download_game.html")
    downloads_html = ''

    if !downloadable_data.empty?
      downloadable_data.each do |platform, data|
        root_dir = GAMES_DIR.sub("#{DATA_DIR}/", '')
        url = "#{root_dir}/#{platform}/#{data}"
        name = "#{platform.capitalize} version"
        downloads_html = "#{downloads_html}#{template.replace('@url', url).replace('@name', name)}"
      end
    end

    # If we have something to download, show the download section.
    if !downloads_html.empty?
      downloads_section = File.read("#{TEMPLATE_DIRECTORY}/snippets/downloads.html")
      downloads_section.sub!('@html', downloads_html)
      html = html.sub('@downloads', downloads_section)
    else
      html = html.sub('@downloads', '')
    end

    return html
  end

  # Modifies "html": replaces @game with in-place game code (<object> for swf, <iframe> for HTML5)
  def __get_inpage_platforms_html(self, g, html)
    in_page_data = platform_data(g, ['flash', 'html5', 'silverlight'])

    if !in_page_data.empty?
      data = in_page_data[:html5] || in_page_data[:flash] || in_page_data[:silverlight]  # html5 first, then flash -- not both
      platform = :html5 if in_page_data.key?(:html5)
      platform = :flash if in_page_data.key?(:flash)
      platform = :silverlight if in_page_data.key?(:silverlight)
      throw "Not sure how to process platform: #{in_page_data}" if platform.None?
      
      # Common to flash/html5/silverlight
      template = File.read("#{TEMPLATE_DIRECTORY}/snippets/#{platform}.html")
      template = template.replace('@width', data['width'].to_s)
      template = template.replace('@height', data['height'].to_s)
      

      if platform == :flash
        template = template.replace('@swf', "games/flash/#{data['swf']}")
      elsif platform == :html5
        template = template.replace('@folder', data['folder'])
      elsif platform == :silverlight
        template = template.replace('@xap', "games/silverlight/#{data['xap']}")
      else
        raise "Not sure how to get in-page data for #{platform}"
      end
      html = html.sub('@game', template)
    else
      # get rid of @game if it's still around
      html = html.replace('@game', '')
    end

    return html
  end

  def __generate_front_page_game_entries(self):
    featured_html = ''
    regular_html = ''
    platform_html = ''

    for g in self.games:
      is_featured = g == self.games[0] || g == self.games[1]
      column_size = is_featured ? 6 : 4 # featured = half-screen, otherwise one-third
      # Regardless of extension, add size
      filename = g['screenshot']

      game_image = "#{IMAGES_DIR}/#{filename}"
      raise "Can't find image #{g['screenshot']} for #{g['name']} in #{IMAGES_DIR}" unless File.exist?(game_image)
      html = "<a href='#{url_for_game(g)}'><img class='img-responsive' src='#{game_image.sub('data/', '')}' /></a>"
      game_dir = GAMES_DIR.sub("#{DATA_DIR}/", '')

      platform_html = ""
      g['platforms'].each do |platform_data|
        platform_data.each do |platform, data|
          # windows/linux: value = executable
          # android: value = google play ID
          # flash: value = { :width, :height, :swf }
          # silverlight: value = xap file
          link_target = "#{game_dir}/#{platform}/#{data}" if ['windows', 'linux'].include?(platform)
          link_target = "#{GOOGLE_PLAY_PATH}#{data}" if platform == 'android'
          link_target = url_for_game(g) if ['flash', 'html5', 'silverlight'].include?(platform)
          
          ext = platform == 'silverlight' ? 'png' : 'svg'
          platform_html = "#{platform_html}<a href='#{link_target}'><img src='images/#{platform}.#{ext}' width='32' height='32' /></a>"
        end
      end

      # Compose final HTML
      final_html = "<div class='col-sm-#{column_size}'>#{html}<br />#{platform_html}</div>"

      if (is_featured)
        featured_html = "#{featured_html}#{final_html}"
      else
        regular_html = "#{regular_html}#{final_html}"
      end
    end

    featured_html = File.read(JUMBOTRON_SNIPPET).sub('@content', featured_html)
    html = File.read("#{OUTPUT_DIR}/#{INDEX_PAGE}")
    html = self.master_page_html.sub(CONTENT_PLACEHOLDER, "#{featured_html}#{regular_html}").replace('@title', 'Home')
    File.write("#{OUTPUT_DIR}/#{INDEX_PAGE}", html)
    FileUtils.cp_r "#{IMAGES_DIR}/.", "#{OUTPUT_DIR}/images"
  end

  # Generates static pages from data/static_pages/*.md
  # Converts them into HTML, links them in the header
  def __generate_static_pages(self):
    raise 'Pages are not defined!' if self.pages.None?

    for p in self.pages:
      markdown = File.read(p)
      to_html = Kramdown::Document.new(markdown).to_html
      html = self.master_page_html.sub(CONTENT_PLACEHOLDER, to_html).replace('@title', to_title(get_page_name(p)))
      page_name = get_page_name(p)
      File.write("#{OUTPUT_DIR}/#{page_name}.html", html)
    end

    puts "Generated #{self.games.count} games and #{self.pages.count} static pages."
  end

  # Generates the "master page" which contains all the common information
  # (eg. header, footer, navbar); content plugs into this. For now, we're
  # using/abusing this by calling it index.html
  def __generate_master_page(self):
    # Get a list of all static pages. We need links for our header.
    index_page = File.read("#{OUTPUT_DIR}/#{INDEX_PAGE}")
    # Naively, sort alphabetically. That usually makes sense.
    self.pages = Dir.glob("#{STATIC_PAGES_DIR}/*.md").sort
    navbar_template = File.read(NAVBAR_LINK_SNIPPET)
    links_html = ''

    for page in self.pages:
      # Create the header link for this page
      # Creates relative links. This is okay, since our site is flat (no subdirectories)
      page_name = get_page_name(page)
      html = navbar_template.replace('@url', "#{page_name}.html").replace('@title', to_title(page_name))
      links_html = "#{links_html}#{html}"
    end

    self.master_page_html = index_page.replace(NAVBAR_LINKS_PLACEHOLDER, links_html)
  end

### start: make a Game class and put these inside

   # page file: eg. data/pages/privacy_policy.md
   # returns: 'privacy_policy'
  def __get_page_name(markdown_filename):
    name_start = markdown_filename.rindex('/') + 1
    name_stop = markdown_filename.rindex('.md')
    page_name = markdown_filename[name_start, name_stop - name_start]
    return page_name
  end

  # g => { :name => 'Quest for the Royal Jelly'}
  # return: quest-for-the-royal-jelly.html
  def __url_for_game(g)
    name = g['name']
    name = name.replace(' ', '-').replace('_', '-').replace("'", "").downcase.strip.chomp
    return "#{name}.html"
  end

  # Get all datapoints for specific platforms. If you pass in (g, ['windows', 'linux']),
  # you'll get data for both windows and linux (if they're both there).
  # HTML5, Flash, and Silverlight need to be shown in-page.
  # Windows, Linux, and Mac need a download link.
  # Returns an array, eg. {:windows => ..., :linux => ...}
  def __platform_data(g, target_platforms)
    to_return = {}

    g['platforms'].each do |platform_data|
      platform_data.each do |platform, data|
        # if you specify both, returns the first one found
        if target_platforms.include?(platform)
            to_return[platform.to_sym] = data
        end
      end
    end    

    return to_return
  end

### end: make a Game class and put these inside

  # privacy_policy => Privacy Policy
  # who_is_that_person => Who is that Person
  def __to_title(sentence)
    stop_words = %w{a an and the or for of nor} #there is no such thing as a definite list of stop words, so you may edit it according to your needs.
    sentence.replace('_', ' ').split.each_with_index.map{|word, index| stop_words.include?(word) && index > 0 ? word : word.capitalize }.join(" ")
  end
end
