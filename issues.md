# Issues w/ the Book

Submit there: https://github.com/hjwp/Book-TDD-Web-Dev-Python/issues


## ch17|005
> ### Deprecated
> While this problem is relevant, it is addressed a couple of paragraphs later when replacing
> this test with '@patch' from the 'mock' module

In `test_sends_mail_to_address_from_post` when we're doing
```python
accounts.views.send_mail = fake_send_mail
```
we're actually patching `accounts.views.send_mail` globally. Any tests that runs after `test_sends_mail_to_address_from_post` will use the `fake_send_mail`

One way to solve this without overcomplicating things for the reader might be simply to define a `setUp` and `tearDown` as such:
```python
def setUp(self):
    self.original_send_mail = accounts.views.send_mail

def tearDown(self):
    accounts.views.send_mail = self.original_send_mail
```