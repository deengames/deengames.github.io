require 'fileutils'
require './src/builder'

desc "Create the website based on data and files."
task :build do
  Builder.new.build
end

desc "Delete all the previously published artifacts"
task :clean do
   Dir.glob('bin/**/*').each do |f|
     f = f['bin/'.length, f.length]
     FileUtils.rm_rf f
   end

   FileUtils.rm_rf 'bin'
   Dir.glob("*.html").each { |f| FileUtils.rm(f) }
   puts 'Cleaned.'
end

desc "Copies all the built binaries to the root directory"
task :publish do
  FileUtils.cp_r 'bin/.', '.'
end

# set default task: build the website
task :default => ['clean', 'build', 'publish']
