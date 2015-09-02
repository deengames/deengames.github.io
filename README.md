[Website](http://deengames.github.io)

# Adding a New game

- Add the vitals to `data/games.yaml`. Copy the structure of the existing ones.
  - For Flash games, you specify the `swf`, `width`, and `height`. They show up on the game details page. (Copy the SWF to `data/games/flash`)
  - For HTML5/JS games, you specify the `folder`, `width`, and `height`. They show up on the game details page in an iFrame.  (Copy the game folder to `data/games/html5`, and make sure there's an `index.html` page.)
  - For Windows/Linux/Mac games, you specify the executable file. Copy it to `data/games/@platform`
  - For Android games, you specify the ID for Google Play
  - For iOS games, I don't know.
  - For Silverlight games, stop, and use something else. Or specify the XAP filename and copy it to `data/games/silverlight`
- Create the right-sized images in `images`. Right now, these are:
  - `<game name>-featured.png` (450x278)
  - `<game name>-normal.png` (290x179)
- run `rake`.
- Verify results locally. If it works, push.
