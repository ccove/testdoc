/**
 * Created by Administrator on 2016/7/17.
 */
var windowWidth=$(window).width();
var windowHeight=$(window).height();
$(function(){
    $(".box").css({
        width:windowWidth,
        height:windowHeight
    });

 $(".main_input input").focus(function(){
     $(this).css({
         backgroundColor:"#fafec0"
     });
     $(this).parent().find('img').show();

 }) ;
    $(".main_input img").click(function(){
        $(".main_input input").val("");
    });
  $(".main_input input").blur(function(){
        $(this).css({
           backgroundColor:"#fff"
        });
        $(".main_input img").hide();

   }) ;
});