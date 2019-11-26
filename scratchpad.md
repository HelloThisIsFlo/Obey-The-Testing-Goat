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


[ ] Save the owner on the List
[ ] Retrieve the lists for a specific owner



1) Add owner to list
2) Save owner when saving list
3) Add endpoint for retrieving list for logged-in user
4) Display on the page


[x] 1) Display on the page
[x] 2) Add endpoint for retrieving list for logged-in user
[ ] 3) Save owner when saving list
[ ] 4) Add owner to list


------------------------
[x] `my_lists` view
  [x] passes the logged in user as 'owner'

[ ] `List` model
  [ ] has `name` attribute
  [ ] has a `User` ForeignKey

[ ] `new_list` view
  [ ] If logged in, create new list with owner

[ ] `NewListFromItemForm` 
  [ ] `__init__` takes `first_list_item`
  [ ] `save` creates a new list, adds the item and save to the DB
  [ ] `saved_list` returns the saved list
  [ ] Invalid form contains errors
