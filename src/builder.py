import distutils.dir_util
import glob
import io
import json
import os.path
import shutil
import time

# Custom code
import src.file_io as file_io

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
    start = time.time()
    self.__verify_files_exist()
    self.__load_data()
    self.__generate_site()
    stop = time.time()
    print("Done in {0} seconds.").format(stop - start)

  def __load_data(self):
    raw_json = file_io.read(Builder.DATABASE_FILE)

    # sort by publication date, reverse chronologically
    self.games = json.loads(raw_json)['games']
    self.games.sort(key = lambda x: x["published"], reverse = True)
    if self.games == None:
        raise(Exception('JSON structure changed; where is the top-level "games" list?'))

  def __verify_files_exist(self):
    if not os.path.isfile(Builder.DATABASE_FILE):
        raise(Exception("#{DATABASE_FILE} not found"))
    if not os.path.isdir(Builder.TEMPLATE_DIRECTORY):
        raise(Exception("#{TEMPLATE_DIRECTORY} directory not found"))

  def __generate_site(self):
    # Copy over CSS, fonts, JS, and the index page, plus site-wide images, etc.
    distutils.dir_util.copy_tree(Builder.TEMPLATE_DIRECTORY, Builder.OUTPUT_DIR)
    for exclusion in Builder.TEMPLATE_EXCLUSIONS:        
        shutil.rmtree("{0}/{1}".format(Builder.OUTPUT_DIR, exclusion))          
    distutils.dir_util.copy_tree(Builder.GAMES_DIR, Builder.OUTPUT_DIR)
    distutils.dir_util.copy_tree(Builder.GUIDES_DIR, Builder.OUTPUT_DIR)

    self.__generate_master_page()
    self.__generate_static_pages()
    self.__generate_front_page_game_entries()
    self.__generate_game_pages()

  def __generate_game_pages(self):
    for g in self.games:
      html = file_io.read(Builder.GAME_PAGE_TEMPLATE)

      version = '1.0.0'      
      if 'version' in g:
          version = g['version']

      html = html.replace('@name', g['name']).replace('@blurb', g['blurb']).replace('@version', version)

      # Start adding per-platform HTML
      # For HTML5 and Flash, add in-page game playing
      html = get_inpage_platforms_html(g, html)
      html = get_downloadable_platforms_html(g, html)
      html = get_mobile_links(g, html)
      html = get_screenshots(g, html)
      html = get_educators_guide(g, html)
      final_html = self.master_page_html.replace(CONTENT_PLACEHOLDER, html).replace('@title', g['name'])
      filename = url_for_game(g)

      file_io.write("{0}/{1}".format(OUTPUT_DIR, filename), final_html)
 
  def __get_educators_guide(self, g, html):
    link = ''
    if 'educators_guide' in g:
      link = "<br /><a href='guides/#{g['educators_guide']}'><img src='images/educators_guide.svg' width='32' height='32' /> Parents/Educators Guide</a>";
    end
    html = html.replace('@educators_guide', link)
    return html

  # Replace @screenshots with screenshots
  def __get_screenshots(self, g, html):
    if 'screenshots' in g:
      template = file_io.read(SCREENSHOTS_SNIPPET)
      name = url_for_game(g).replace('.html', '')
      ss_html = ''
      for s in g['screenshots']:
        url = "images/#{name}/#{s}"
        native_size = FastImage.size("data/#{url}") # [w, h]
        if native_size == None:
            raise(Exception("Can't get native size of images/#{name}/#{s}"))
        # Scale to 250px. Unless the image is already smaller. Then don't scale.
        scale = [1.0 * MAX_SCREENSHOT_SIZE / native_size[0],  1.0 * MAX_SCREENSHOT_SIZE / native_size[1], 1].min
        scale_w = (scale * native_size[0]).to_i
        scale_h = (scale * native_size[1]).to_i
        ss_html = "#{ss_html}<img src='#{url}' width='#{scale_w}' height='#{scale_h}' data-jslghtbx='#{url}' class='screenshot' />"
      template = template.replace('@screenshots', ss_html)
      html = html.replace('@screenshots', template)
    else:
      html = html.replace('@screenshots', '')

    return html

  # Modifies "html": replaces @mobile with mobile links
  def __get_mobile_links(self, g, html):
    links_html = ''
    mobile_data = __platform_data(g, ['android']) #TODO: iOS
    if not mobile_data: # empty?
      for platform, data in mobile_data.items():
        link_target = "#{GOOGLE_PLAY_PATH}#{data}"
        links_html += "<a href='#{link_target}'><img src='images/google-play-badge.png' /></a>"
      
      html = html.replace('@mobile', links_html)
    else:
      html = html.replace('@mobile', '')
    
    return html

  # Modifies "html": replaces @downloads with download links
  def __get_downloadable_platforms_html(self, g, html):
    downloadable_data = __platform_data(g, ['windows', 'linux', 'mac'])
    template = file_io.read("#{TEMPLATE_DIRECTORY}/snippets/download_game.html")
    downloads_html = ''

    if not downloadable_data: #empty?
      for platform, data in downloadable_data.items():
        root_dir = GAMES_DIR.replace("#{DATA_DIR}/", '')
        url = "#{root_dir}/#{platform}/#{data}"
        name = "#{platform.capitalize} version"
        downloads_html = "#{downloads_html}#{template.replace('@url', url).replace('@name', name)}"
      
    

    # If we have something to download, show the download section.
    if not downloads_html: #empty?
      downloads_section = file_io.read("#{TEMPLATE_DIRECTORY}/snippets/downloads.html")
      downloads_section = downloads_section.replace('@html', downloads_html)
      html = html.replace('@downloads', downloads_section)
      html = html.replace('@downloads', '')

    return html

  # Modifies "html": replaces @game with in-place game code (<object> for swf, <iframe> for HTML5)
  def __get_inpage_platforms_html(self, g, html):
    in_page_data = __platform_data(g, ['flash', 'html5', 'silverlight'])

    if not in_page_data: #empty?
      data = in_page_data["html5"] or in_page_data["flash"] or in_page_data["silverlight"]  # html5 first, then flash -- not both
      if "html5" in in_page_data:
          platform = "html5" 
      if "flash" in in_page_data:
          platform = "flash"
      if "silverlight" in in_page_data:
        platform = "silverlight" 
      if platform == None:
        raise(Exception("Not sure how to process platform: #{in_page_data}"))
      
      # Common to flash/html5/silverlight
      template = file_io.read("#{TEMPLATE_DIRECTORY}/snippets/#{platform}.html")
      template = template.replace('@width', data['width'].to_s)
      template = template.replace('@height', data['height'].to_s)
      

      if platform == "flash":
        template = template.replace('@swf', "games/flash/#{data['swf']}")
      elif platform == "html5":
        template = template.replace('@folder', data['folder'])
      elif platform == "silverlight":
        template = template.replace('@xap', "games/silverlight/#{data['xap']}")
      else:
        raise(Exception("Not sure how to get in-page data for #{platform}"))
      
      html = html.replace('@game', template)
    else:
      # get rid of @game if it's still around
      html = html.replace('@game', '')
    
    return html

  def __generate_front_page_game_entries(self):
    featured_html = ''
    regular_html = ''
    platform_html = ''

    for g in self.games:
      is_featured = g == self.games[0] or g == self.games[1]
      column_size = 6 if is_featured else 4 # featured = half-screen, otherwise one-third
      # Regardless of extension, add size
      filename = g['screenshot']

      game_image = "#{IMAGES_DIR}/#{filename}"
      if not os.path.isfile(game_image):
        raise(Exception("Can't find image {0} for {1} in {2}".format(g['screenshot'], g['name'], Builder.IMAGES_DIR)))
      html = "<a href='#{url_for_game(g)}'><img class='img-responsive' src='#{game_image.replace('data/', '')}' /></a>"
      game_dir = GAMES_DIR.replace("{0}/".format(DATA_DIR), '')

      platform_html = ""
      for platform_data in g['platforms']:
        for platform, data in platform_data.items():
          # windows/linux: value = executable
          # android: value = google play ID
          # flash: value = { :width, :height, :swf }
          # silverlight: value = xap file
          if 'windows' in platform or 'linux' in platform:
            link_target = "#{game_dir}/#{platform}/#{data}"
          elif 'android' in platform:
            link_target = "#{GOOGLE_PLAY_PATH}#{data}"
          elif 'flash' in platform or 'html5' in platform or 'silverlight' in platform:
            link_target = url_for_game(g)
          else:
            raise(Exception("Not sure what the link target is for {0}".format(platform)))
          
          ext = ('png' if platform == 'silverlight' else 'svg')
          platform_html = "#{platform_html}<a href='#{link_target}'><img src='images/#{platform}.#{ext}' width='32' height='32' /></a>"

      # Compose final HTML
      final_html = "<div class='col-sm-#{column_size}'>#{html}<br />#{platform_html}</div>"

      if is_featured:
        featured_html = "#{featured_html}#{final_html}"
      else:
        regular_html = "#{regular_html}#{final_html}"

    featured_html = file_io.read(JUMBOTRON_SNIPPET).replace('@content', featured_html)
    html = file_io.read("#{OUTPUT_DIR}/#{INDEX_PAGE}")
    html = self.master_page_html.replace(CONTENT_PLACEHOLDER, "#{featured_html}#{regular_html}").replace('@title', 'Home')
    file_io.write("#{OUTPUT_DIR}/#{INDEX_PAGE}", html)
    distutils.dir_util.copy_tree("#{IMAGES_DIR}/.", "#{OUTPUT_DIR}/images")

  # Generates static pages from data/static_pages/*.md
  # Converts them into HTML, links them in the header
  def __generate_static_pages(self):
    if self.pages == None:
        raise(Exception('Pages are not defined!'))

    for p in self.pages:
      raw_markdown = file_io.read(p)
      to_html = markdown.markdown(raw_markdown)
      html = self.master_page_html.replace(Builder.CONTENT_PLACEHOLDER, to_html).replace('@title', Builder.__to_title(Builder.__get_page_name(p)))
      page_name = Builder.__get_page_name(p)

      file_io.write("{0}/{1}.html".format(Builder.OUTPUT_DIR, page_name), html)

    print("Generated #{self.games.count} games and #{self.pages.count} static pages.")

  # Generates the "master page" which contains all the common information
  # (eg. header, footer, navbar); content plugs into this. For now, we're
  # using/abusing this by calling it index.html
  def __generate_master_page(self):
    # Get a list of all static pages. We need links for our header.
    index_page = file_io.read("{0}/{1}".format(Builder.OUTPUT_DIR, Builder.INDEX_PAGE))
    # Naively, sort alphabetically. That usually makes sense.
    self.pages = glob.glob("{0}/*.md".format(Builder.STATIC_PAGES_DIR))
    self.pages.sort()

    navbar_template = file_io.read(Builder.NAVBAR_LINK_SNIPPET)
    
    links_html = ''

    for page in self.pages:
      # Create the header link for this page
      # Creates relative links. This is okay, since our site is flat (no subdirectories)
      page_name = Builder.__get_page_name(page)
      html = navbar_template.replace('@url', "#{page_name}.html").replace('@title', Builder.__to_title(page_name))
      links_html = "#{links_html}#{html}"
    

    self.master_page_html = index_page.replace(Builder.NAVBAR_LINKS_PLACEHOLDER, links_html)

### start: make a Game class and put these inside

   # page file: eg. data/pages/privacy_policy.md
   # returns: 'privacy_policy'
  def __get_page_name(markdown_filename):
    name_start = markdown_filename.rindex('/') + 1
    name_stop = markdown_filename.rindex('.md')
    page_name = markdown_filename[name_start:name_stop]
    return page_name

  # g => { :name => 'Quest for the Royal Jelly'}
  # return: quest-for-the-royal-jelly.html
  def __url_for_game(g):
    name = g['name']
    name = name.replace(' ', '-').replace('_', '-').replace("'", "").downcase.strip.chomp
    return "#{name}.html"

  # Get all datapoints for specific platforms. If you pass in (g, ['windows', 'linux']),
  # you'll get data for both windows and linux (if they're both there).
  # HTML5, Flash, and Silverlight need to be shown in-page.
  # Windows, Linux, and Mac need a download link.
  # Returns an array, eg. {:windows => ..., :linux => ...}
  def __platform_data(g, target_platforms):
    to_return = {}

    for platform_data in g['platforms']:
      for platform, data in platform_data.items():
        # if you specify both, returns the first one found
        if platform in target_platforms:
            to_return[platform.to_sym] = data

    return to_return

### end: make a Game class and put these inside

  # privacy_policy => Privacy Policy
  # who_is_that_person => Who is that Person
  def __to_title(sentence):
    stop_words = ['a', 'an', 'and', 'the', 'or', 'for', 'of', 'nor'] #there is no such thing as a definite list of stop words, so you may edit it according to your needs.
    words = sentence.replace('_', ' ').split()
    
    for word in words:
        word = word.capitalize() if word in stop_words else word

    return ', '.join([str(w) for w in words]) 
