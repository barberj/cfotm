Ext.application({
    name: 'CFOTM',

    launch: function() {
        Ext.create("Ext.tab.Panel", {
            fullscreen: true,
            tabBarPosition: 'bottom',

            items: [
                {
                    xtype: 'nestedlist',
                    title: 'WODS',
                    iconCls: 'star',
                    displayField: 'wod_date',

                    store: {
                        type: 'tree',

                        fields: [
                            'wod_date', 'wod', 'created_at',
                            {name: 'leaf', defaultValue: true}
                        ],

                        root: {
                            leaf: false
                        },

                        proxy: {
                            type: 'rest',
                            url: '/wods',
                            reader: {
                                type: 'json',
                            }
                        }
                    },

                    detailCard: {
                        xtype: 'panel',
                        scrollable: true,
                        styleHtmlContent: true
                    },

                    listeners: {
                        itemtap: function(nestedList, list, index, element, post) {
                            this.getDetailCard().setHtml(post.get('wod'));
                        }
                    }
                }
            ]
        });
    }
});

