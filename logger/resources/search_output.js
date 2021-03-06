function outputSearch(caller)
{
    // The parameter caller may be wither the search bar or the checkbox for
    // "show duplicates"
    var input, filter, code, pre, i, txtValue, lastTxtValue, checkbox, showDuplicates;
    for (i = 0; i < caller.parentNode.childNodes.length; i++)
    {
        if (caller.parentNode.childNodes[i].type == "checkbox")
        {
            checkbox = caller.parentNode.childNodes[i];
        }
        if (caller.parentNode.childNodes[i].type == "text")
        {
            input = caller.parentNode.childNodes[i];
        }
    }
    filter = input.value.toUpperCase();
    code = document.getElementById(input.getAttribute("target"));
    pre = code.getElementsByTagName("pre");
    div = code.querySelectorAll('[line-number]');
    showDuplicates = checkbox.checked;


    // Loop through all code rows, and hide those who don't match the
    // search query
    for (i = 0; i < pre.length; i++)
    {
        txtValue = pre[i].textContent || pre[i].innerText;
        txtValue = txtValue.replaceAll("<[^>]*>", "");
        txtValue = txtValue.replaceAll("\u2060", "").toUpperCase();
        if (!filter ||
            (txtValue.match(filter) && (!(txtValue === lastTxtValue) ||
                                        showDuplicates)))
        {
            pre[i].style.display = "";
            div[i].style.display = "";
            lastTxtValue = txtValue;
        }
        else
        {
            pre[i].style.display = "none";
            div[i].style.display = "none";
        }
    }
}
