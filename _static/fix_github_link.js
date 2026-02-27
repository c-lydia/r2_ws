// Replace incorrect Edit-on-GitHub links that reference a non-existent 'maindocs' ref
(function(){
  try {
    var anchors = document.querySelectorAll('a.fa.fa-github');
    anchors.forEach(function(a){
      if(a.href && a.href.indexOf('/blob/main/docs/source/') !== -1){
        a.href = a.href.replace('/blob/main/docs/source/', '/blob/main/docs/source/');
      }
    });
  } catch (e) {
    console.error('fix_github_link.js error', e);
  }
})();
