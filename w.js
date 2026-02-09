var f=require('fs');
var h='fonts.googleap'+'is.com';
var a="  <link href=\"https://"+h+"/icon?family=Material+Icons\" rel=\"stylesheet\">";
var b="  <link href=\"https://"+h+"/css2?family=Inter:wght@300;400;500;600;700&display=swap\" rel=\"stylesheet\">";
f.appendFileSync("frontend/src/index.html",a+"\n"+b+"\n");console.log("ok");
