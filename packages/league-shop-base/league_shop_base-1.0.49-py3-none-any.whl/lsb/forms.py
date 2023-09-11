from django import forms


class ProductStatusRemarksForm(forms.Form):
    status = forms.CharField(initial="unchanged", required=False)
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": "5"}),
        initial="unchanged",
    )
