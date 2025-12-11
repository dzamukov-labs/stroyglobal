<?php
$to = 'info@stroyglobal.com, georgij-dzamukov@yandex.ru';
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
		<form action="" method="POST" id="form-data">
				<input type="hidden" name="url" value="" id="page-url">
				<div><input class="input" name="username" required placeholder="Ваше имя*"></div>
				<div><input class="input" name="useremail" placeholder="Ваш e-mail"></div>
				<div><input class="input" name="phone" required placeholder="Ваш телефон*"></div>
				<div><textarea rows="6" name="msg" placeholder="Ваше сообщение"></textarea></div>
			<input type="submit" value="Отправить" />
		</form>
	<?php

}