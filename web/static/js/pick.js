
var bloodhound = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: repositories,
});

function matchWithDefaults(q, sync) {
    if (q === '') {
	sync(bloodhound.get(repositories));
    } else {
	bloodhound.search(q, sync);
    }
}

$('.typeahead').typeahead({
    hint: true,
    minLength: 0,
    highlight: true,
}, {
    name: 'respositories',
    source: matchWithDefaults,
});
