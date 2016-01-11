$( document ).ready(function()
{
    // Initializes the search UI
    $('.ui.search')
        .search
    (
        {
            apiSettings:
            {
                beforeSend: function (settings)
                {
                    // Subscribe to comments collection, and will filter based on the value
                    // the user typed in the search box, and also stop the last subscription
                    try
                    {
                        commentSubscribe.stop();
                    } catch(err) {}
                    commentSubscribe = Meteor.subscribe("comments", $('.ui.search').search('get value'), $('.ui.dropdown').dropdown('get value'));

                    // Changes a header showing the user what was searched
                    $('#userSearch').text($('.ui.search').search('get value'));

                    // Add a loading icon to the search bar before we sent our request
                    // to the tornado server
                    $('.ui.search').addClass("loading");

                    // If the dropdown value is 0, it means that we are searching
                    // by username, if the dropdown value is 1, then it means we are searching
                    // by channel ID
                    if ($('.ui.dropdown').dropdown('get value') == "1")
                    {
                        // If searching by channel ID, then we will populate the ID portion
                        // of the request
                        settings.url = settings.url + 'name=&id='
                            + $('.ui.search').search('get value');
                    }
                    else if ($('.ui.dropdown').dropdown('get value') == "0")
                    {
                        // If searching by user name, then we will populate the name portion
                        // of the request
                        settings.url = settings.url + 'id=&name='
                            + $('.ui.search').search('get value');
                    }

                    // returns the setting.url that we have modified
                    return settings;
                },
                // Base URL settings, according to the dropdown, we will either populate a
                // Channel ID or user name, but not both (limitation of youtube API v3)
                url: window.location.href+"/channel?";
            }
        }
    )

    // Initialize a dropdown, so that users can select between Channel ID, and User Name
    // if dropdown is not initialized, it will not work
    $('.ui.dropdown').dropdown({});
});
