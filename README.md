[View Website](http://deengames.github.io)

# Adding a New game

- Add the vitals to `data/games.yaml`. Copy the structure of the existing ones.
  - For Flash games, you specify the `swf`, `width`, and `height`. They show up on the game details page. (Copy the SWF to `data/games/flash`)
    - eg. `{ ... platforms: { flash: { swf: ..., width: ..., height: ... } } }`
  - For HTML5/JS games, you specify the `folder`, `width`, and `height`. They show up on the game details page in an iFrame.  (Copy the game folder to `data/games/html5`, and make sure there's an `index.html` page.)
  - For Windows/Linux/Mac games, you specify the executable file. Copy it to `data/games/@platform`
  - For Android games, you specify the ID for Google Play
  - For iOS games, I don't know.
  - For Silverlight games, stop, and use something else. Specify the XAP filename and size `{ xap: ..., width: ..., height: ... }` and copy it to `data/games/silverlight`
- Create an image in `data/images/<game name>.png`. This image should be 450x278. (It's scaled down when not featured.)
- run `rake`.
- Verify results locally. If it works, push.

# Repository Organization

GitHub Pages sites demand that the actual content is in the `master` branch. As such, source code is in the `source` branch.