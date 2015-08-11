require 'json'
require 'fileutils'
require 'kramdown'

class Builder

  OUTPUT_DIR = 'bin'
  DATA_DIR = 'data'
  DATABASE_FILE = "#{DATA_DIR}/games.yaml"

  STATIC_PAGES_DIR = "#{DATA_DIR}/static_pages"
  TEMPLATE_DIRECTORY = 'templates'
  # Copy the template dir. But not these items.
  TEMPLATE_EXCLUSIONS = ['snippets']

  INDEX_PAGE = 'index.html'
  NAVBAR_LINKS_PLACEHOLDER = '<!-- DG navbar links -->'
  NAVBAR_LINK_SNIPPET = "#{TEMPLATE_DIRECTORY}/snippets/navbar_link.html"
  CONTENT_PLACEHOLDER = '<!-- DG content -->'

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
    @games = JSON.parse(File.read(DATABASE_FILE))['games']
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
    generate_pages
  end

  def generate_pages
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

    # TODO: make the real index page
    FileUtils.rm "#{OUTPUT_DIR}/#{INDEX_PAGE}"
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
