<?php
header('Content-Type: text/html;charset=utf-8');
$to = 'info@stroyglobal.com';
if(isset($_POST['username'])){
	$un = htmlspecialchars(@$_POST['username']);
	$ue = htmlspecialchars(@$_POST['useremail']);
	$up = htmlspecialchars(@$_POST['phone']);
	$um = nl2br(htmlspecialchars(@$_POST['msg']));
	$ok = mail($to,'Feedback',"User:$un<br>\nemail:$ue<br>\nphone:$up<br>\n-----------------<br>\n$um","MIME-Version: 1.0\r\nContent-type: text/html; charset=utf-8\r\n");
	if($ok){
		echo 'Ваше сообщение отправлено';
	} else {
		echo 'Ваше сообщение НЕ отправлено, попробуйте ещё раз.';
	}
} else {
	?>