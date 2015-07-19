require 'json'

class Main

  DATABASE_FILE = 'data/games.yaml'
  TEMPLATE_DIRECTORY = 'templates'

  def run
    verify_files_exist
    generate_data
  end

  private

  def verify_files_exist
    raise "#{DATABASE_FILE} not found" unless File.exist?(DATABASE_FILE)
    raise "#{TEMPLATE_DIRECTORY} directory not found" unless Dir.exists?(TEMPLATE_DIRECTORY)
  end

  def generate_data
    games = JSON.parse(File.read(DATABASE_FILE))
    games = games['list']
    games.each do |g|
      puts "#{g} => #{game_name_to_token(g)}"
    end
  end

  def game_name_to_token(name)
    return name.gsub(' ', '-').gsub('_', '-').downcase.strip.chomp
  end
end

Main.new.run
