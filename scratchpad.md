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
[x] Clean up `wait_for` stuff in `base.py`

[x] NewListFromItemForm
  [x] Accepts data in constructor
  [x] Save w/ no arguments
    [x] Saves new list with item as first element
    [x] Saves owner if present
    [x] Owner is optional
    [x] Returns saved list
  [x] Blank items are invalid

[x] Re-implement `test_validation_errors_are_show_on_home_page` as integration test

[x] List.create_new
  [x] Creates new list
  [x] First item of the list is `first_item_text`
  [x] Optionally adds owner to list
