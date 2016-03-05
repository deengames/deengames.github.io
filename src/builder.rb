require 'json'
require 'fileutils'
require 'time'

# Gems
require 'kramdown'
require 'fastimage'

class Builder

  OUTPUT_DIR = 'bin' # where to build to
  DATA_DIR = 'data' # where our data files are
  DATABASE_FILE = "#{DATA_DIR}/games.json"
  STATIC_PAGES_DIR = "#{DATA_DIR}/static_pages"
  IMAGES_DIR = "#{DATA_DIR}/images"
  GAMES_DIR = "#{DATA_DIR}/games"

  TEMPLATE_DIRECTORY = 'templates'
  # We copy the template dir. But not these items.
  TEMPLATE_EXCLUSIONS = ['snippets']

  INDEX_PAGE = 'index.html' # the home index page; this is also the layout.
  NAVBAR_LINKS_PLACEHOLDER = '<!-- DG navbar links -->' # Where the navbar list of pages goes
  # Snippets where we put in real data (eg. game page URLs)
  NAVBAR_LINK_SNIPPET = "#{TEMPLATE_DIRECTORY}/snippets/navbar_link.html"
  JUMBOTRON_SNIPPET = "#{TEMPLATE_DIRECTORY}/snippets/jumbotron.html"
  CONTENT_PLACEHOLDER = '<!-- DG content -->' # Where in the template we fill in the page content
  GAME_PAGE_TEMPLATE = "#{TEMPLATE_DIRECTORY}/game.html"

  GOOGLE_PLAY_PATH = 'https://play.google.com/store/apps/details?id=' # URL for Google Play
  
  # When scaling images, scale down to this width/height (whatever's smaller)
  # The image width (if a landscape image) is guaranteed to be 250px or less
  # The image height (if a portrait image) is guaranteed to be 250px or less
  MAX_SCREENSHOT_SIZE = 250 

  def build
    start = Time.new
    verify_files_exist
    load_data
    generate_site
    stop = Time.new
    puts "Done in #{stop - start} seconds."
  end

  private

  def load_data
    @games = JSON.parse(File.read(DATABASE_FILE))['games'].sort! {
      # sort by publication date, reverse chronologically
      |x, y| Time.parse(y['published']) <=> Time.parse(x['published'])
    }
    raise 'JSON structure changed; where is the top-level "games" list?' if @games.nil?
  end

  def verify_files_exist
    raise "#{DATABASE_FILE} not found" unless File.exist?(DATABASE_FILE)
    raise "#{TEMPLATE_DIRECTORY} directory not found" unless Dir.exist?(TEMPLATE_DIRECTORY)
  end

  def generate_site
    # Copy over CSS, fonts, JS, and the index page, plus site-wide images, etc.
    FileUtils.cp_r "#{TEMPLATE_DIRECTORY}/.", OUTPUT_DIR
    TEMPLATE_EXCLUSIONS.each do |exclusion|
      FileUtils.rm_rf exclusion
    end
    FileUtils.cp_r GAMES_DIR, OUTPUT_DIR

    generate_master_page
    generate_static_pages
    generate_front_page_game_entries
    generate_game_pages
  end

  def generate_game_pages
    @games.each do |g|
      html = File.read("#{GAME_PAGE_TEMPLATE}")
      html = html.gsub('@name', g['name']).gsub('@blurb', g['blurb'])

      # Start adding per-platform HTML
      # For HTML5 and Flash, add in-page game playing
      html = get_inpage_platforms_html(g, html)
      html = get_downloadable_platforms_html(g, html)
      html = get_mobile_links(g, html)
      html = get_screenshots(g, html)
      final_html = @master_page_html.sub(CONTENT_PLACEHOLDER, html).gsub('@title', g['name'])      
      filename = url_for_game(g)
      File.open("#{OUTPUT_DIR}/#{filename}", 'w') { |f| f.write(final_html) }
    end
  end

  # Replace @screenshots with screenshots
  def get_screenshots(g, html)    
    if !g['screenshots'].nil?
      ss_html = "<h2>Screenshots</h2>" # Mixing HTML and code is bad, dude.
      name = url_for_game(g).sub('.html', '')
      g['screenshots'].each do |s|
        url = "images/#{name}/#{s}"
        native_size = FastImage.size("data/#{url}") # [w, h]
        # Scale to 250px. Unless the image is already smaller. Then don't scale.
        scale = [1.0 * MAX_SCREENSHOT_SIZE / native_size[0],  1.0 * MAX_SCREENSHOT_SIZE / native_size[1], 1].min
        scale_w = (scale * native_size[0]).to_i
        scale_h = (scale * native_size[1]).to_i
        ss_html = "#{ss_html}<img src='#{url}' width='#{scale_w}' height='#{scale_h}' data-jslghtbx='#{url}' />"
      end
      html = html.gsub('@screenshots', ss_html)
    else
      html = html.gsub('@screenshots', '')
    end    
    return html
  end

  # Modifies "html": replaces @mobile with mobile links
  def get_mobile_links(g, html)    
    links_html = ''
    mobile_data = platform_data(g, ['android']) #TODO: iOS
    if !mobile_data.empty?      
      mobile_data.each do |platform, data|        
        link_target = "#{GOOGLE_PLAY_PATH}#{data}"
        links_html += "<a href='#{link_target}'><img src='images/google-play-badge.png' /></a>"
      end
      html = html.gsub('@mobile', links_html)
    else
      html = html.gsub('@mobile', '')
    end    
    return html
  end
  
  # Modifies "html": replaces @downloads with download links
  def get_downloadable_platforms_html(g, html)
    downloadable_data = platform_data(g, ['windows', 'linux', 'mac'])
    template = File.read("#{TEMPLATE_DIRECTORY}/snippets/download_game.html")
    downloads_html = ''

    if !downloadable_data.empty?
      downloadable_data.each do |platform, data|
        root_dir = GAMES_DIR.sub("#{DATA_DIR}/", '')
        url = "#{root_dir}/#{platform}/#{data}"
        name = "#{platform.capitalize} version"
        downloads_html = "#{downloads_html}#{template.gsub('@url', url).gsub('@name', name)}"
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
  def get_inpage_platforms_html(g, html)
    in_page_data = platform_data(g, ['flash', 'html5'])

    if !in_page_data.empty?
      data = in_page_data[:html5] || in_page_data[:flash]  # html5 first, then flash -- not both
      platform = :html5 if in_page_data.key?(:html5)
      platform = :flash if platform.nil?

      # Common to flash/html5
      template = File.read("#{TEMPLATE_DIRECTORY}/snippets/#{platform}.html")
      template = template.gsub('@width', data['width'].to_s)
      template = template.gsub('@height', data['height'].to_s)

      if platform == :flash
        template = template.gsub('@swf', "games/flash/#{data['swf']}")
      elsif platform == :html5
        template = template.gsub('@folder', data['folder'])
      else
        raise "Not sure how to get in-page data for #{platform}"
      end
      html = html.sub('@game', template)
    else
      # get rid of @game if it's still around
      html = html.gsub('@game', '')
    end

    return html
  end

  def generate_front_page_game_entries
    featured_html = ''
    regular_html = ''
    platform_html = ''

    @games.each do |g|
      is_featured = g == @games[0] || g == @games[1]
      column_size = is_featured ? 6 : 4 # featured = half-screen, otherwise one-third
      # Regardless of extension, add size
      filename = g['screenshot']

      game_image = "#{IMAGES_DIR}/#{filename}"
      raise "Can't find image #{g['screenshot']} for #{g['name']} in #{IMAGES_DIR}" unless File.exist?(game_image)
      html = "<a href='#{url_for_game(g)}'><img class='img-responsive' src='#{game_image.sub('data/', '')}' /></a>"

      platform_html = ""
      g['platforms'].each do |platform_data|
        # TODO: switch to SVGs for these
        platform_data.each do |platform, data|
          # windows/linux: value = executable
          # android: value = google play ID
          # flash: value = { :width, :height, :swf }
          link_target = "#{GAMES_DIR}/#{platform}/#{data}" if ['windows', 'linux'].include?(platform)
          link_target = "#{GOOGLE_PLAY_PATH}#{data}" if platform == 'android'
          link_target = url_for_game(g) if ['flash', 'html5'].include?(platform)
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
    html = @master_page_html.sub(CONTENT_PLACEHOLDER, "#{featured_html}#{regular_html}").gsub('@title', 'Home')
    File.write("#{OUTPUT_DIR}/#{INDEX_PAGE}", html)
    FileUtils.cp_r "#{IMAGES_DIR}/.", "#{OUTPUT_DIR}/images"
  end

  # Generates static pages from data/static_pages/*.md
  # Converts them into HTML, links them in the header
  def generate_static_pages
    raise 'Pages are not defined!' if @pages.nil?

    @pages.each do |p|
      markdown = File.read(p)
      to_html = Kramdown::Document.new(markdown).to_html
      html = @master_page_html.sub(CONTENT_PLACEHOLDER, to_html).gsub('@title', to_title(get_page_name(p)))
      page_name = get_page_name(p)
      File.write("#{OUTPUT_DIR}/#{page_name}.html", html)
    end

    puts "Generated #{@pages.count} pages."
  end

  # Generates the "master page" which contains all the common information
  # (eg. header, footer, navbar); content plugs into this. For now, we're
  # using/abusing this by calling it index.html
  def generate_master_page
    # Get a list of all static pages. We need links for our header.
    index_page = File.read("#{OUTPUT_DIR}/#{INDEX_PAGE}")
    # Naively, sort alphabetically. That usually makes sense.
    @pages = Dir.glob("#{STATIC_PAGES_DIR}/*.md").sort
    navbar_template = File.read(NAVBAR_LINK_SNIPPET)
    links_html = ''

    @pages.each do |page|
      # Create the header link for this page
      # Creates relative links. This is okay, since our site is flat (no subdirectories)
      page_name = get_page_name(page)
      html = navbar_template.gsub('@url', "#{page_name}.html").gsub('@title', to_title(page_name))
      links_html = "#{links_html}#{html}"
    end

    @master_page_html = index_page.gsub(NAVBAR_LINKS_PLACEHOLDER, links_html)
  end

### start: make a Game class and put these inside

   # page file: eg. data/pages/privacy_policy.md
   # returns: 'privacy_policy'
  def get_page_name(markdown_filename)
    name_start = markdown_filename.rindex('/') + 1
    name_stop = markdown_filename.rindex('.md')
    page_name = markdown_filename[name_start, name_stop - name_start]
    return page_name
  end

  # g => { :name => 'Quest for the Royal Jelly'}
  # return: quest-for-the-royal-jelly.html
  def url_for_game(g)
    name = g['name']
    name = name.gsub(' ', '-').gsub('_', '-').downcase.strip.chomp
    return "#{name}.html"
  end

  # Get all datapoints for specific platforms. If you pass in (g, ['windows', 'linux']),
  # you'll get data for both windows and linux (if they're both there).
  # HTML5 and Flash need to be shown in-page.
  # Windows, Linux, and Mac need a download link.
  # Returns an array, eg. {:windows => ..., :linux => ...}
  def platform_data(g, target_platforms)
    to_return = {}

    g['platforms'].each do |platform_data|
      platform_data.each do |platform, data|
        # if you specify both, returns the first one found
        to_return[platform.to_sym] = data if target_platforms.include?(platform)
      end
    end

    return to_return
  end

### end: make a Game class and put these inside

  # privacy_policy => Privacy Policy
  # who_is_that_person => Who is that Person
  def to_title(sentence)
    stop_words = %w{a an and the or for of nor} #there is no such thing as a definite list of stop words, so you may edit it according to your needs.
    sentence.gsub('_', ' ').split.each_with_index.map{|word, index| stop_words.include?(word) && index > 0 ? word : word.capitalize }.join(" ")
  end
end
