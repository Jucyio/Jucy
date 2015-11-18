

function customTokenizer(datum) {
    var repository = datum.substring(datum.indexOf('/') + 1);
    return [datum, repository];
}

var bloodhound = new Bloodhound({
    datumTokenizer: customTokenizer,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: repositories,
});

bloodhound.initialize()

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
    name: 'repositories',
    source: matchWithDefaults,
});
