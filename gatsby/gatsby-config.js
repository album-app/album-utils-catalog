module.exports = {
  pathPrefix: `/album-utils-catalog/`,
  siteMetadata: {
    title: 'album utils catalog',
    subtitle: 'sharing album utility solutions across tools and domains',
    catalog_url: 'https://github.com/album-app/album-utils-catalog',
    menuLinks:[
      {
         name:'Catalog',
         link:'/catalog'
      },
      {
         name:'About',
         link:'/about'
      },
    ]
  },
  plugins: [{ resolve: `gatsby-theme-album`, options: {} }],
}
