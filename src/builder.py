import distutils.dir_util
import glob
import io
import json
import os
import shutil
import time

# Custom code
import src.file_io as file_io

# Extensions
import markdown
from PIL import Image

class Builder:

    OUTPUT_DIR = 'bin' # where to build to
    DATA_DIR = 'data' # where our data files are
    DATABASE_FILE = os.path.join(DATA_DIR, "games.json")
    STATIC_PAGES_DIR = os.path.join(DATA_DIR, "static_pages")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    GAMES_DIR = "games"
    GUIDES_DIR = "guides"

    TEMPLATE_DIRECTORY = 'templates'
    # We copy the template dir. But not these items.
    TEMPLATE_EXCLUSIONS = ['snippets']
    # Copy these from the root to bin
    INDIVIDUAL_FILES_TO_COPY = ['CNAME', 'favicon.ico']

    INDEX_PAGE = 'index.html' # the home index page; this is also the layout.
    NAVBAR_LINKS_PLACEHOLDER = '<!-- DG navbar links -->' # Where the navbar list of pages goes
    # Snippets where we put in real data (eg. game page URLs)
    NAVBAR_LINK_SNIPPET = os.path.join(TEMPLATE_DIRECTORY, "snippets", "navbar_link.html")
    JUMBOTRON_SNIPPET = os.path.join(TEMPLATE_DIRECTORY, "snippets", "jumbotron.html")
    SCREENSHOTS_SNIPPET = os.path.join(TEMPLATE_DIRECTORY, "snippets", "screenshots.html")
    CONTENT_PLACEHOLDER = '<!-- DG content -->' # Where in the template we fill in the page content
    GAME_PAGE_TEMPLATE = os.path.join(TEMPLATE_DIRECTORY, "game.html")

    GOOGLE_PLAY_PATH = 'https://play.google.com/store/apps/details?id=' # URL for Google Play

    ITCH_IO_URL_ROOT = 'https://deengames.itch.io'
    STEAM_ROOT_URL = 'https://store.steampowered.com/app'

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
        print("Done in {0} seconds.".format(stop - start))

    def __load_data(self):
        raw_json = file_io.read(Builder.DATABASE_FILE)
        json_games = json.loads(raw_json)['games']
        
        if json_games == None:
            raise(Exception('JSON structure changed; where is the top-level "games" list?'))

        # sort by publication date, reverse chronologically (newest first)
        json_games.sort(key = lambda x: x["published"], reverse = True)

        # Convert into Game instances
        self.games = []
        for j in json_games:
            if "ignore" in j and j["ignore"] != "false":
                print("Skipping {}".format(j["name"]))
            else:
                self.games.append(Game(j)) 

    def __verify_files_exist(self):
        if not os.path.isfile(Builder.DATABASE_FILE):
            raise(Exception("{0} not found".format(Builder.DATABASE_FILE)))
        if not os.path.isdir(Builder.TEMPLATE_DIRECTORY):
            raise(Exception("{0} directory not found".format(Builder.TEMPLATE_DIRECTORY)))

    def __generate_site(self):
        # Delete the old output (clean build)
        shutil.rmtree(Builder.OUTPUT_DIR, True)
        
        # Copy over CSS, fonts, JS, and the index page, plus site-wide images, etc.
        distutils.dir_util.copy_tree(Builder.TEMPLATE_DIRECTORY, Builder.OUTPUT_DIR)
        for exclusion in Builder.TEMPLATE_EXCLUSIONS:                
            shutil.rmtree(os.path.join(Builder.OUTPUT_DIR, exclusion), True)

        # Copy individual files
        for item in Builder.INDIVIDUAL_FILES_TO_COPY:
            shutil.copyfile(item, os.path.join(Builder.OUTPUT_DIR, item))

        self.__generate_master_page()
        self.__generate_static_pages()
        self.__generate_front_page_game_entries()

    def __generate_front_page_game_entries(self):
        featured_html = ''
        regular_html = ''
        platform_html = ''
        in_this_row = 0

        for g in self.games:
            is_featured = g == self.games[0]
             
            # featured = full-screen, otherwise one-third
            # also, featured image requires center-block class to center. Otherwise, whitespace on the RHS.
            column_size = 12 if is_featured else 4
            image_class = 'img-responsive center-block' if is_featured else 'img-responsive'
            # Regardless of extension, add size
            filename = g.get('screenshot')

            game_image = os.path.join(Builder.IMAGES_DIR, filename)
            if not os.path.isfile(game_image):
                raise(Exception("Can't find image {2}/{0} for game {1}".format(g.get('screenshot'), g.get('name'), Builder.IMAGES_DIR)))
            html = "<a href='{0}'><img class='{1}' src='{2}' /></a>".format(g.get_url(), image_class, game_image.replace('{0}{1}'.format(Builder.DATA_DIR, os.sep), ''))

            platform_html = ""
            # Some games have only a custom URL and no platforms; ignore those.
            if g.has("platforms"):
                for platform_data in g.get('platforms'):
                    for platform, data in platform_data.items():
                        # windows/linux: value = executable
                        # android: value = google play ID
                        # flash: value = { :width, :height, :swf }
                        # silverlight: value = xap file
                        if 'windows' in platform or 'linux' in platform or 'mac' in platform:
                            link_target = "{0}/{1}/{2}".format(Builder.GAMES_DIR, platform, data)
                        elif 'android' in platform:
                            link_target = "{0}{1}".format(Builder.GOOGLE_PLAY_PATH, data)
                        elif 'flash' in platform or 'html5' in platform or 'silverlight' in platform:
                            link_target = g.get_url()
                        else:
                            print("WARNING: Not sure what the link target is for {0}".format(platform))
                        
                        ext = ('png' if platform == 'silverlight' else 'svg')
                        platform_html = "{0}<img src='images/{1}.{2}' width='32' height='32' />".format(platform_html, platform, ext)

            # Compose final HTML
            final_html = "<div class='col-sm-{0}'>{1}{2}</div>".format(column_size, html, platform_html)

            if not is_featured:
                if in_this_row == 0:
                    final_html = "{0}{1}".format("<div class='row'>", final_html)
                elif in_this_row == 2:
                    final_html = "{0}{1}".format(final_html, "</div>")

                in_this_row += 1
                in_this_row %= 3

            if is_featured:
                featured_html = "{0}\r\n{1}".format(featured_html, final_html)
            else:
                regular_html = "{0}\r\n{1}".format(regular_html, final_html)

            

        # close unopened div if number of games is not divisible by 3
        if (in_this_row > 0):
            regular_html += "</div>"

        featured_html = file_io.read(Builder.JUMBOTRON_SNIPPET).replace('@content', featured_html)
        html = file_io.read(os.path.join(Builder.OUTPUT_DIR, Builder.INDEX_PAGE))
        html = self.master_page_html.replace(Builder.CONTENT_PLACEHOLDER, "{0}{1}".format(featured_html, regular_html)).replace('@title', 'Home')
        file_io.write(os.path.join(Builder.OUTPUT_DIR, Builder.INDEX_PAGE), html)
        distutils.dir_util.copy_tree(os.path.join(Builder.IMAGES_DIR, "."), os.path.join(Builder.OUTPUT_DIR, "images"))

    # Generates static pages from data/static_pages/*.md
    # Converts them into HTML, links them in the header
    def __generate_static_pages(self):
        if self.pages == None:
                raise(Exception('Pages are not defined!'))

        for p in self.pages:
            raw_markdown = file_io.read(p)
            to_html = markdown.markdown(raw_markdown)
            html = self.master_page_html.replace(Builder.CONTENT_PLACEHOLDER, to_html).replace('@title', self.__to_title(self.__get_page_name(p)))
            page_name = self.__get_page_name(p)

            file_io.write(os.path.join(Builder.OUTPUT_DIR, "{0}.html".format(page_name)), html)

        print("Generated {0} games and {1} static pages.".format(len(self.games), len(self.pages)))

    # Generates the "master page" which contains all the common information
    # (eg. header, footer, navbar); content plugs into this. For now, we're
    # using/abusing this by calling it index.html
    def __generate_master_page(self):
        # Get a list of all static pages. We need links for our header.
        index_page = file_io.read(os.path.join(Builder.OUTPUT_DIR, Builder.INDEX_PAGE))
        # Naively, sort alphabetically. That usually makes sense.
        self.pages = glob.glob(os.path.join(Builder.STATIC_PAGES_DIR, "*.md"))
        self.pages.sort()

        navbar_template = file_io.read(Builder.NAVBAR_LINK_SNIPPET)
        
        links_html = ''

        for page in self.pages:
            if "\\draft" in page:
                print("Skipping static page draft for {}".format(page))
            else:
                # Create the header link for this page
                # Creates relative links. This is okay, since our site is flat (no subdirectories)
                page_name = self.__get_page_name(page)
                html = navbar_template.replace('@url', "{0}.html".format(page_name)).replace('@title', self.__to_title(page_name))
                links_html = "{0}{1}".format(links_html, html)

        self.master_page_html = index_page.replace(Builder.NAVBAR_LINKS_PLACEHOLDER, links_html)

     # page file: eg. data/pages/privacy_policy.md
     # returns: 'privacy_policy'
    def __get_page_name(self, markdown_filename):
        name_start = markdown_filename.rindex(os.sep) + 1
        name_stop = markdown_filename.rindex('.md')
        page_name = markdown_filename[name_start:name_stop]
        return page_name

    # privacy_policy => Privacy Policy
    # who_is_that_person => Who is that Person
    def __to_title(self, sentence):
        stop_words = ['a', 'an', 'and', 'the', 'or', 'for', 'of', 'nor'] #there is no such thing as a definite list of stop words, so you may edit it according to your needs.
        words = sentence.replace('_', ' ').split()

        title = ""
        for word in words:
            if word not in stop_words:
                word = word.capitalize()
            title = "{0}{1} ".format(title, word)
        return title.strip()

class Game:
    def __init__(self, json):
        self.json = json

    def has(self, key):
        return key in self.json

    def get(self, key):
        return self.json[key]
    
    # Get all datapoints for specific platforms. If you pass in (['windows', 'linux']),
    # you'll get data for both windows and linux (if the game has data for both).
    # HTML5, Flash, and Silverlight need to be shown in-page.
    # Windows, Linux, and Mac need a download link.
    # Returns an array, eg. {:windows => ..., :linux => ...}
    def platform_data(self, target_platforms):
        to_return = {}

        for platform_data in self.get('platforms'):
            for platform, data in platform_data.items():
                # if you specify multiple, returns the first one found
                if platform in target_platforms:
                    to_return[platform] = data

        return to_return   

    ### REGION: URL and HTML responsibilities ###

    
    # HTML for @game for in-place games (Flash, HTML5/JS, Silverlight).
    # Generates <object> for Flash/Silverlight, <iframe> for HTML5
    def get_inpage_platforms_html(self, template_directory):
        in_page_data = self.platform_data(['flash', 'html5', 'silverlight'])

        if in_page_data: # not empty
            platform = None
            # html5 first, then flash -- not both
            if "html5" in in_page_data:
                platform = "html5" 
                data = in_page_data["html5"]
            if "flash" in in_page_data:
                platform = "flash"
                data = in_page_data["flash"]
            if "silverlight" in in_page_data:
                platform = "silverlight" 
                data = in_page_data["silverlight"]
            if platform == None:
                raise(Exception("Not sure how to process platform: {0}".format(in_page_data)))
            
            # Common to flash/html5/silverlight
            template = file_io.read(os.path.join(template_directory, "snippets", "{0}.html".format(platform)))
            template = template.replace('@width', str(data['width']))
            template = template.replace('@height', str(data['height']))

            if platform == "flash":
                template = template.replace('@swf', "games/flash/{0}".format(data['swf']))
            elif platform == "html5":
                template = template.replace('@folder', data['folder'])
            elif platform == "silverlight":
                template = template.replace('@xap', "games/silverlight/{0}".format(data['xap']))
            else:
                raise(Exception("Not sure how to get in-page data for {0}".format(platform)))
            
            return template
        else:
            return "";        


    # Download links for @downloads, if applicable (desktop only)
    def get_downloadable_platforms_html(self, template_directory, games_directory):
        downloadable_data = self.platform_data(['windows', 'linux', 'mac'])
        template = file_io.read(os.path.join(template_directory, "snippets", "download_game.html"))
        downloads_html = ''

        if downloadable_data: # not empty
            for platform, data in downloadable_data.items():
                url = "{0}/{1}/{2}".format(games_directory, platform, data)
                name = "{0} version".format(platform.capitalize())
                downloads_html = "{0}{1}".format(downloads_html, template.replace('@url', url).replace('@name', name))

        # If we have something to download, show the download section. (Separate template.)
        if downloads_html: # not empty
            downloads_section = file_io.read(os.path.join(template_directory, "snippets", "downloads.html"))
            downloads_section = downloads_section.replace('@html', downloads_html)
            return downloads_section
        else:
            return ""


    # Mobile links for @mobile, if applicable (mobile apps only)
    def get_mobile_links(self, google_play_prefix):
        links_html = ''
        mobile_data = self.platform_data(['android']) #TODO: iOS
        if mobile_data: # not empty
            for platform, data in mobile_data.items():
                link_target = "{0}{1}".format(google_play_prefix, data)
                links_html += "<a href='{0}'><img src='images/google-play-badge.png' /></a>".format(link_target)
            
            return links_html
        else:
            return ""

    # Screenshot HTML for @screenshots
    def get_screenshots(self):
        if self.has('screenshots'):
            template = file_io.read(Builder.SCREENSHOTS_SNIPPET)
            name = self.get_url().replace('.html', '')
            ss_html = ''
            for s in self.get('screenshots'):
                url = os.path.join("images", name, s)
                native_size = Image.open(os.path.join("data", url)).size # (w, h)
                # Scale to 250px. Unless the image is already smaller. Then don't scale.
                scale = min(1.0 * Builder.MAX_SCREENSHOT_SIZE / native_size[0], 1.0 * Builder.MAX_SCREENSHOT_SIZE / native_size[1], 1)
                scale_w = int(scale * native_size[0])
                scale_h = int(scale * native_size[1])
                ss_html = "{0}<img src='{1}' width='{2}' height='{3}' data-jslghtbx='{1}' class='screenshot' />".format(ss_html, url, scale_w, scale_h)
            
            return template.replace('@screenshots', ss_html)
        else:
            return ""        

    # return: Quest for the Royal Jelly => quest-for-the-royal-jelly
    def get_url(self):
        if self.has("steamAppId"):
            steamAppId = self.get("steamAppId")
            return "{}/{}".format(Builder.STEAM_ROOT_URL, steamAppId)
        elif self.has("customUrl"):
            return self.get("customUrl")
        else:
            name = self.get('name')
            name = name.replace(' ', '-').replace('_', '-').replace("'", "").lower().strip()
            return "{}/{}".format(Builder.ITCH_IO_URL_ROOT, name)

    def get_educators_guide_html(self):
        if self.has('educators_guide'):
            return "<br /><a href='guides/{0}'><img src='images/educators_guide.svg' width='32' height='32' /> Parents/Educators Guide</a>".format(self.get('educators_guide'))
        else:
            return ""
    