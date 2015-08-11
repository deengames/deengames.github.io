require 'fileutils'
require './src/builder'

desc "Create the website based on data and files."
task :build do
  Builder.new.build
end

task :clean do
   Dir.glob('templates/*').each do |dir|
     dir = dir['templates/'.length, dir.length]
     FileUtils.rm_rf dir
   end

   Dir.glob("*.html").each { |f| FileUtils.rm(f) }
   puts 'Cleaned.'
end

# set default task: build the website
task :default => ['clean', 'build']
