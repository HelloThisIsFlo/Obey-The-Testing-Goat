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


[x] New Feature / FT: Only logged in users can see their list
  [x] Not logged in -> Can not access someone else list
  [x] Not logged in -> Can not access someone else 'My lists'
  [x] Logged in -> Can not access someone else list
  [x] Logged in -> Can not access someone else 'My lists'

[x] Remove duplication in `forms`


## Sharing

Before going w/ the 'Sharing' model way, explore 'ManyToMany' in Spike


[ ] Feature / FT
  [ ] User doesn't exist error

[x] List View
  [x] Passes SharingForm in `share_form`

[x] Share View
  [x] Creates a SharingForm & call save (no is_valid for now)
  [x] Redirects to list

---- Can implement until here, then think a bit more

[x] SharingForm
  [x] placeholder: "your-friend@example.com"
  [x] Takes list_id & data['email'] in init
  [x] Call `List.add_sharee(list_id=..., email=...)` on save
  [x] Returns updated list on save


[x] `list_.add_sharee(email=...)` - Non-mocked tests
  [x] Adds sharee
      (This will test it saves, but also that it 'can' save a list of sharee)