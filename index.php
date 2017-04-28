<html>
<head>
<title>My UDT</title>
</head>
<body style="text-align:center">
<font  face="微软雅黑" >
<font size="5">User Device Tracker</font>
</p>
<TABLE style="BORDER-TOP-STYLE: solid; BORDER-RIGHT-STYLE: solid; BORDER-LEFT-STYLE: solid; BORDER-BOTTOM-STYLE: solid" borderColor=#4a4a84 height=40 cellSpacing=8 cellPadding=2 width=800 align=center bgColor=#ffffff border=2>
<TBODY>
<TR>
<TD style="BORDER-RIGHT: #4a4a84 2px dashed; BORDER-TOP: #4a4a84 2px dashed; BACKGROUND: #ffffff; BORDER-LEFT: #4a4a84 2px dashed; BORDER-BOTTOM: #4a4a84 2px dashed">
<DIV align=center>


<form action="index.php" method="get">
请输入IP或者MAC: <input type="text" name="content" />
<input name='sub1' type="submit"  value='search'/>
<input name='sub2' type="submit"  value='history'/>
<input name='sub3' type="submit"  value='update'/>
</form>


<?php
$tip = '';
$cont = $_REQUEST['content'];
$sub1 =  $_REQUEST['sub1'];
$sub2 =  $_REQUEST['sub2'];
$sub3 =  $_REQUEST['sub3'];

if ($sub1 != '')
    {
        $sub = $sub1;
    }
if ($sub2 != '')
    {
        $sub = $sub2;
    }
if ($sub3 != '')
    {
        $sub = $sub3;
        $cont = '11.11.11.11';
        $tip = 'update will use 14 minute ,please wait ... ';
    }

//echo $sub;
$str = 'python udt.py '.$cont.' '.$sub;
//echo $str.'</p>';
echo '<font color="red">'.$tip.'</font>';
passthru($str);
?>
</DIV></TD></TR></TBODY></TABLE>
</p>
Designed by yihongfei@dangdang.com
2015.01.19
</font>
</body>
</html>
