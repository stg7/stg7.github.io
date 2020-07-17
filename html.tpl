<!DOCTYPE html>
<html>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="{{author}}">
   <head>
    <title>{{title}}</title>

        <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>

        <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

        <!-- Optional theme -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">

        <!-- Latest compiled and minified JavaScript -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

        <link rel="stylesheet" href="page.css">

        <link href='https://fonts.googleapis.com/css?family=Orbitron:900' rel='stylesheet' type='text/css'>

        <script type="text/javascript">


            function http_get(theUrl) {
                // based on https://stackoverflow.com/a/4033310
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
                xmlHttp.send( null );
                return xmlHttp.responseText;
            }


            function add_top5_repos() {
                request_url = "https://api.github.com/users/stg7/repos?sort=created&type=public";
                console.log(request_url);
                res = JSON.parse(http_get(request_url));
                console.log(res);
                var result_div = document.getElementById("top-5-projects");
                var result_list = document.createElement("ul");

                res.filter(repo => !repo["fork"]).slice(0, 5).forEach(
                    function(repo) {
                        console.log(repo["name"], repo["html_url"], repo["description"]);
                        var list_element = document.createElement("li");
                        list_element.innerHTML = "<a href='" + repo["html_url"] + "' ><font id='reponame'> " + repo["name"] + "</font></a>: " + repo["description"] + "";

                        result_list.append(list_element);

                    }
                )

                result_div.append(result_list);

                //console.log(res);
            }


            document.addEventListener("DOMContentLoaded", function(){
                add_top5_repos();
            });

        </script>
  </head>

  <body>
    <nav class="navbar">
        <div class="container">
            <a href="./index.html" class="logo">{{title}}</a>
            <ul class="nav navbar-nav navbar-right">
                <li>
                    <a href="https://github.com/stg7/" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" style="height:1.5em" />
                    </a>
                </li>
            </ul>
        </div>
    </nav>
    <hr>
    <div class="maincontent">
        <section id="toc" class="container theme-showcase">
        {{toc}}
        </section>
        <hr>
        <section class="container theme-showcase" role="main" style="height:80%">
            {{content}}

        </section>
    </div>

  </body>

</html>
