require 'json'
require 'fileutils'
require 'kramdown'
require 'time'

class Builder

  OUTPUT_DIR = 'bin' # where to build to
  DATA_DIR = 'data' # where our data files are
  DATABASE_FILE = "#{DATA_DIR}/games.yaml"
  STATIC_PAGES_DIR = "#{DATA_DIR}/static_pages"
  IMAGES_DIR = "#{DATA_DIR}/images"

  TEMPLATE_DIRECTORY = 'templates'
  # We copy the template dir. But not these items.
  TEMPLATE_EXCLUSIONS = ['snippets']

  INDEX_PAGE = 'index.html' # the home index page; this is also the layout.
  NAVBAR_LINKS_PLACEHOLDER = '<!-- DG navbar links -->' # Where the navbar list of pages goes
  # Snippets where we put in real data (eg. game page URLs)
  NAVBAR_LINK_SNIPPET = "#{TEMPLATE_DIRECTORY}/snippets/navbar_link.html"
  JUMBOTRON_SNIPPET = "#{TEMPLATE_DIRECTORY}/snippets/jumbotron.html"
  CONTENT_PLACEHOLDER = '<!-- DG content -->' # Where in the template we fill in the page content

  DOWNLOADS_PATH = 'downloads' # location of Windows/Linux binaries
  GOOGLE_PLAY_PATH = 'https://play.google.com/store/apps/details?id=' # URL for Google Play

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

    generate_master_page
    generate_static_pages
    generate_game_entries
  end

  # Generates entries for the front page
  def generate_game_entries
    featured_html = ''
    regular_html = ''
    platform_html = ''

    @games.each do |g|
      is_featured = g == @games[0] || g == @games[1]
      type = is_featured ? 'featured' : 'regular'
      column_size = is_featured ? 6 : 4 # featured = half-screen, otherwise one-third
      # Regardless of extension, add size
      filename = g['screenshot']
      ['png', 'jpg'].each do |format|
        filename.sub!(".#{format}", "-#{type}.#{format}")
      end

      game_image = "#{IMAGES_DIR}/#{filename}"
      raise "Can't find image #{g['screenshot']} for #{g['name']} in #{IMAGES_DIR}" unless File.exist?(game_image)
      html = "<a href='#{game_name_to_token(g['name'])}.html'><img class='img-responsive' src='#{game_image.sub('data/', '')}' /></a>"

      platform_html = ""
      g['platforms'].each do |p|
        # TODO: switch to SVGs for these
        p.keys.each do |platform|
          binary_path = p[platform]
          binary_path = "#{DOWNLOADS_PATH}/#{platform}/#{binary_path}" if ['windows', 'linux'].include?(platform)
          binary_path = "#{GOOGLE_PLAY_PATH}#{p[platform]}" if platform == 'android'
          platform_html = "#{platform_html}<a href='#{binary_path}'><img src='images/#{platform}.png' /></a>"
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
    html = @master_page_html.sub(CONTENT_PLACEHOLDER, "#{featured_html}#{regular_html}")
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
      html = @master_page_html.sub(CONTENT_PLACEHOLDER, to_html)
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

   # page file: eg. data/pages/privacy_policy.md
   # returns: 'privacy_policy'
  def get_page_name(markdown_filename)
    name_start = markdown_filename.rindex('/') + 1
    name_stop = markdown_filename.rindex('.md')
    page_name = markdown_filename[name_start, name_stop - name_start]
    return page_name
  end

  def game_name_to_token(name)
    return name.gsub(' ', '-').gsub('_', '-').downcase.strip.chomp
  end

  # privacy_policy => Privacy Policy
  # who_is_that_person => Who is that Person
  def to_title(sentence)
    stop_words = %w{a an and the or for of nor} #there is no such thing as a definite list of stop words, so you may edit it according to your needs.
    sentence.gsub('_', ' ').split.each_with_index.map{|word, index| stop_words.include?(word) && index > 0 ? word : word.capitalize }.join(" ")
  end
end
