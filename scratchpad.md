[x] Do not save blank items for every request
[x] Code smell: POST test is too long?
[x] Display multiple items in the table
[x] Clean up after FT runs
[x] Remove `time.sleep` in FT
[x] Allow multiple lists for multiple users

[x] Support more than one list
  [x] Adjust model so that items are associated with different lists
  [x] Add unique URLs for each list
  [x] Add a URL for creating a new list via POST
  [x] Add URLs for adding a new item to an existing list via POST
  [x] Refactor away some duplication in `urls.py`

[x] Remove hardcoded URLs from `views.py`
[x] Remove hardcoded URLs from `list.html` & `home.html`
[x] Remove duplication of validation logic in views

[ ] Make 'uid' in Token non-editable