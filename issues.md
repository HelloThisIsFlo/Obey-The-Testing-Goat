# Issues w/ the Book
To translate to Github Issues once I know where to submit them

## ch07l006 - Useless assertion
Anyway, initially I just wanted to comment on a minor detail. In ch07l006, there is an useless assertion that sneaked in. 
Basically, that test: self.assertNotIn('make a fly', page_text) is useless because in test_multiple_users_can_start_lists_at_different_urls Edith did not create a second list item with '...make a fly'. So that particular assertion would never fail and just brings a little bit of confusion.

# Page 187 (Kindle version) - Confusing shell command
```bash
elspeth@server:$ set -a; source .env; set +a
```
It would be nice to explain the `set -a;` & `set +a`. I found out by googling.

# Page 226: `lists/tests/test_model.py`
It's a bit confusing when you write:
```python
item.save()
item.full_clean()
```
while the name of the tests is `test_cannot_save_empty_list_item`
Because in the end... the item is saved. It can be verified by putting the following right after the with block:
```python
self.assertEqual(Item.objects.count(), 0)
```

So maybe, just swapping the order of the 2 lines might make things less confusing :)

```python
item.full_clean()
item.save()
```

Another solution would be to simply rename the tests from `test_cannot_save_empty_list_item` to `test_cannot_validate_empty_list_item`
And removing the call to `save()` alltogether.


# ch11l032
This is introduced, to test the HTML5 validation:

```python
self.wait_for(lambda: self.browser.find_elements_by_css_selector(
 '#id_text:invalid'
 ))
```

However, it isn't testing anything. 

Because we are using `find_elementS_by_css_selector(...)` if the element is not found an empty list will be returned and no exception will be raised. Therefore our `wait_for` immediately returns after the first try and we didn't test anything (try making it fail on purpose by looking for a different id, it won't fail).

To fix that, the solution is simple, remove the `S`. That way it'll either find that one element, or raise a `NoSuchElementException`, which is a `WebDriverException`, so our `wait_for` works as expected 🙂
