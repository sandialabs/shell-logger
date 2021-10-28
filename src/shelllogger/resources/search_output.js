function outputSearch(caller)
{
    // The parameter caller may be wither the search bar or the checkbox for
    // "show duplicates"
    var input, filter, table, tr, td, i, txtValue, lastTxtValue, showDuplicates, showNeighbors;
    for (i = 0; i < caller.parentNode.childNodes.length; i++)
    {
        if (caller.parentNode.childNodes[i].type == "checkbox")
        {
            var checkbox = caller.parentNode.childNodes[i]
            if (checkbox.name.toLowerCase().indexOf("duplicate") > -1)
            {
                showDuplicates = caller.parentNode.childNodes[i].checked;
            }
            if (checkbox.name.toLowerCase().indexOf("neighbor") > -1)
            {
                showNeighbors = caller.parentNode.childNodes[i].checked;
            }
        }
        if (caller.parentNode.childNodes[i].type == "text")
        {
            input = caller.parentNode.childNodes[i];
        }
    }
    filter = input.value.toUpperCase();
    table = document.getElementById(input.getAttribute("target"));
    tr = table.getElementsByTagName("tr");
    lastTxtValue = null
    neighborOpacity = [
        { offset: -3, opacity: 0.40 },
        { offset: -2, opacity: 0.50 },
        { offset: -1, opacity: 0.60 },
        { offset:  1, opacity: 0.60 },
        { offset:  2, opacity: 0.50 },
        { offset:  3, opacity: 0.40 },
    ]
    matchingIndexes = []

    // Loop through all table rows, and hide those who don't match the
    // search query
    for (i = 0; i < tr.length; i++)
    {
        td = tr[i].getElementsByTagName("td");
        txtValue = td[1].textContent || td[1].innerText;
        txtValue = txtValue.replaceAll("<[^>]*>", "").toUpperCase();
        if (!filter ||
            (txtValue.match(filter) && (!(txtValue === lastTxtValue) ||
                                        showDuplicates)))
        {
            tr[i].style.display = "";
            tr[i].style.opacity = 1.0;
            lastTxtValue = txtValue;
            matchingIndexes.push(i)
        }
        else
        {
            tr[i].style.display = "none";
            tr[i].style.opacity = 0.0;
        }
    }
    lastTxtValue = null
    if (showNeighbors)
    {
        for (const i of matchingIndexes)
        {
            for (const op of neighborOpacity)
            {
                j = Math.min(Math.max(i+op.offset, 0), tr.length-1)
                tr[j].style.display = "";
                tr[j].style.opacity = Math.max(tr[j].style.opacity, op.opacity);
            }
        }
    }
}
