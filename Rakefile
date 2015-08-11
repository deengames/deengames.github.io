require './src/builder'

desc "Create the website based on data and files."
task :build do
  Builder.new.build
end

# set default task: build the website
task :default => ['build']
