require 'json'
require 'fileutils'

desc "Create the website based on data and files."
task :build do
  games = JSON.parse(File.read('data/games.yaml'))
  games = games['games']  
end

# set default task: build the website
task :default => ['build']
