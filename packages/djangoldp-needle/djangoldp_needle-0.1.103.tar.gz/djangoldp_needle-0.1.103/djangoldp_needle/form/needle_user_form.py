from djangoldp_account.forms import LDPUserForm
import uuid

class NeedleUserForm(LDPUserForm):
    def __init__(self, *args, **kwargs):
        super(LDPUserForm, self).__init__(*args, **kwargs)

        # Remove field from form and validation
        self.fields['username'].validators = []
        self.fields['username'].required = False

    def save(self, commit=True):
        # Auto generate username as UUID
        self.instance.username = str(uuid.uuid4())

        return super(LDPUserForm, self).save(commit)
