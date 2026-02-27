// Replace incorrect Edit-on-GitHub links that reference a non-existent 'maindocs' ref
(function(){
  try {
    var repoRoot = 'https://github.com/c-lydia/r2_ws.git';

    // Fix Edit-on-GitHub links that point to an incorrect path
    var editLinks = document.querySelectorAll('a.fa.fa-github');
    editLinks.forEach(function(a){
      if(a.href && a.href.indexOf('/blob/maindocs/source/') !== -1){
        a.href = a.href.replace('/blob/maindocs/source/', '/blob/main/docs/source/');
      }
    });

    // Replace breadcrumb aside link to point to repository root (open in new tab)
    var aside = document.querySelector('.wy-breadcrumbs-aside');
    if(aside){
      var repoLink = aside.querySelector('a');
      if(repoLink){
        repoLink.href = repoRoot;
        repoLink.textContent = 'Repository';
        repoLink.setAttribute('target','_blank');
        repoLink.setAttribute('rel','noopener');
        repoLink.classList.remove('fa');
        repoLink.classList.remove('fa-github');
      }
    }
  } catch (e) {
    console.error('fix_github_link.js error', e);
  }
})();
