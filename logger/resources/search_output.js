function outputSearch(caller)
{
    // The parameter caller may be wither the search bar or the checkbox for
    // "show duplicates"
    var input, filter, table, tr, td, i, txtValue, lastTxtValue, checkbox, showDuplicates;
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
    table = document.getElementById(input.getAttribute("target"));
    tr = table.getElementsByTagName("tr");
    showDuplicates = checkbox.checked;


    // Loop through all table rows, and hide those who don't match the
    // search query
    for (i = 0; i < tr.length; i++)
    {
        td = tr[i].getElementsByTagName("td")[0];
        if (td)
        {
            txtValue = td.textContent || td.innerText;
            txtValue = txtValue.replaceAll("<[^>]*>", "");
            txtValue = txtValue.replaceAll("\u2060", "").toUpperCase();
            if (!filter ||
                (txtValue.match(filter) && (!(txtValue === lastTxtValue) ||
                                            showDuplicates)))
            {
                tr[i].style.display = "";
                lastTxtValue = txtValue;
            }
            else
            {
                tr[i].style.display = "none";
            }
        }
    }
}
