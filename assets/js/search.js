/*
 * 559Theme search results renderer (MiniSearch-based; replaces the old Lunr
 * renderer that used to live inline in content/lunr-search.html).
 *
 * Expects, from layouts/search.html:
 *   - window.MiniSearch      — the vendored UMD build (assets/js/minisearch.js)
 *   - window.SEARCH_INDEX_URL — the site's index.json, resolved from baseURL
 *     (not a hard-coded relative path, so this works under any subpath).
 *
 * Builds all result markup via createElement/createTextNode rather than
 * innerHTML, so neither page content nor the user's search string can ever
 * be interpreted as markup.
 */
(function () {
  function onWindowOnload(newFunction) {
    var oldFunction = window.onload;
    window.onload = function (ev) {
      if (oldFunction) oldFunction.apply(window, ev);
      newFunction();
    };
  }

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  onWindowOnload(function () {
    var query = new URLSearchParams(window.location.search);
    var searchString = query.get("q");
    var target = document.getElementById("app");

    function addText(node, text) {
      node.appendChild(document.createTextNode(text));
      return node;
    }
    function addSearchString(node, text) {
      var searchSpan = document.createElement("span");
      searchSpan.classList.add("search__string");
      searchSpan.appendChild(document.createTextNode(text));
      addText(node, ' "');
      node.appendChild(searchSpan);
      addText(node, '" ');
    }
    function addAndAppendPar(etype, parclass) {
      var node = document.createElement(etype);
      if (parclass) node.classList.add(parclass);
      target.appendChild(node);
      return node;
    }

    target.innerHTML = "";

    if (!searchString) {
      addText(addAndAppendPar("p", "search__message"), "Enter a search term in the box above.");
      return;
    }

    var message = addAndAppendPar("p", "search__message");
    addText(message, "Searching for string");
    addSearchString(message, searchString);
    addText(message, " ... loading index data");

    fetch(window.SEARCH_INDEX_URL)
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        addText(message, "Loaded index data - building index for " + data.length + " pages");

        var miniSearch = new MiniSearch({
          idField: "uri",
          fields: ["title", "tags", "content"],
          extractField: function (document, fieldName) {
            var value = document[fieldName];
            return Array.isArray(value) ? value.join(" ") : value;
          },
          searchOptions: {
            boost: { title: 15, tags: 10, content: 5 },
            prefix: true,
            fuzzy: 0.2,
            // AND, not MiniSearch's OR default: with OR, a multi-word query's
            // short/common words (via prefix+fuzzy expansion) match nearly
            // every page (measured: a 2-word query hit 38/45 VisSnacks pages
            // under OR, 1-3 under AND). AND requires every query word to
            // match somewhere in the document, which is what a "search this
            // site" box should do.
            combineWith: "AND",
          },
        });
        miniSearch.addAll(data);
        message.innerText = "";

        var matches = miniSearch.search(searchString);

        if (matches.length) {
          var dataDict = {};
          data.forEach(function (page) {
            dataDict[page.uri] = page;
          });

          addText(message, "String");
          addSearchString(message, searchString);
          addText(message, "found on " + matches.length + " of " + data.length + " pages");

          var listElem = addAndAppendPar("ul", "search__resultlist");
          matches.forEach(function (match) {
            var link = match.id;
            var page = dataDict[link];
            var title = page.title;

            var elem = document.createElement("li");
            elem.classList.add("search__result");
            listElem.appendChild(elem);

            var aElem = document.createElement("a");
            aElem.href = link;
            aElem.title = title;
            addText(aElem, title);
            elem.appendChild(aElem);

            var span = document.createElement("span");
            span.classList.add("search__context");

            var contextSize = 20;
            var content = page.content;
            var re = new RegExp(escapeRegExp(searchString), "i");
            var index = content.search(re);

            if (index >= 0) {
              var preindex = index > contextSize ? index - contextSize : 0;
              var endindex = index + searchString.length;
              var post = endindex + contextSize;

              addText(span, " “" + content.slice(preindex, index));
              var hl = document.createElement("span");
              hl.classList.add("search__string");
              hl.appendChild(document.createTextNode(content.slice(index, endindex)));
              span.appendChild(hl);
              addText(span, content.slice(endindex, post) + "”");
            } else {
              addText(span, " (inexact match)");
            }
            elem.appendChild(span);
          });
        } else {
          addText(message, "String");
          addSearchString(message, searchString);
          addText(message, "not found in " + data.length + " pages");
        }
      })
      .catch(function () {
        addText(addAndAppendPar("p", "search__message"), "Search failed - failed to load and build index");
      });
  });
})();
