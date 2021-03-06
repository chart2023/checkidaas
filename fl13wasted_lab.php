<?php
error_reporting(E_ALL);
require_once ('/var/www/html/jpgraph/src/jpgraph.php');
require_once ('/var/www/html/jpgraph/src/jpgraph_scatter.php');
$now1=date("Y-m-d H:i:s");
$yest=date('Y-m-d',strtotime("-1 days"));
//echo $now1;
DEFINE('fl13','/var/www/html/fl13plan_lab.png');
$zonefl13[0]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z1/analytic/wasted_energy/per_day';
$zonefl13[1]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z2/analytic/wasted_energy/per_day';
$zonefl13[2]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z3/analytic/wasted_energy/per_day';
$zonefl13[3]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z4/analytic/wasted_energy/per_day';
$zonefl13[4]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z5/analytic/wasted_energy/per_day';
$zonefl13[5]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z6/analytic/wasted_energy/per_day';
$zonefl13[6]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z7/analytic/wasted_energy/per_day';
$zonefl13[7]='http://khetnon/eng4/fl13/north/lab_tsrl_dsprl_emrl/z8/analytic/wasted_energy/per_day';
$uuid=uuid();
foreach ($zonefl13 as &$key){
        $wastedresult[]=checkvalue(checkdate1(fetchdata($key,$uuid),$yest));
}
//var_dump($wastedresult);
foreach ($wastedresult as &$key1){
        $colorresult[]=colorresult($key1);
}
function markCallback($y,$x) {
    if( $x == 54 )
    return array(false,false,false,'red',0.8);
    else
    return array(false,false,false,'yellow',2);
}
$data = array(
    array(12,82,50,$colorresult[0]),
    array(12,36,50,$colorresult[1]),
    array(32,82,50,$colorresult[2]),
    array(32,36,50,$colorresult[3]),
        array(55,82,50,$colorresult[4]),
        array(55,36,50,$colorresult[5]),
        array(74,82,50,$colorresult[6]),
        array(74,36,50,$colorresult[7])
);
// We need to create X,Y data vectors suitable for the
// library from the above raw data.
$n = count($data);
for( $i=0; $i < $n; ++$i ) {

    $datax[$i] = $data[$i][0];
    $datay[$i] = $data[$i][1];

    // Create a faster lookup array so we don't have to search
    // for the correct values in the callback function
    $format[strval($datax[$i])][strval($datay[$i])] = array($data[$i][2],$data[$i][3]);

}
function FCallback($aYVal,$aXVal) {
    global $format;
    return array($format[strval($aXVal)][strval($aYVal)][0],'',
         $format[strval($aXVal)][strval($aYVal)][1],'','');
}
//$wastedstring=
// Setup the graph
$graph = new Graph(1920,1280);

// We add a small 1pixel left,right,bottom margin so the plot area
// doesn't cover the frame around the graph.
$graph->img->SetMargin(1,1,1,1);
$graph->SetScale('linlin',0,100,0,100);

// We don't want any axis to be shown
$graph->xaxis->Hide();
$graph->yaxis->Hide();

// Use a worldmap as the background and let it fill the plot area
$graph->SetBackgroundImage(fl13,BGIMG_FILLPLOT);

// Setup a nice title with a striped bevel background
$graph->title->Set("Floor 13 research lab:  Wasted energy ratio (daily update)                   Modified:$now1");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,30);
$graph->title->SetColor('white');
$graph->SetTitleBackground('darkgreen',TITLEBKG_STYLE1,TITLEBKG_FRAME_BEVEL);
$graph->SetTitleBackgroundFillStyle(TITLEBKG_FILLSTYLE_HSTRIPED,'blue','darkgreen');
// Finally create the scatterplot
$sp = new ScatterPlot($datay,$datax);
//$sp->value->Show();
// We want the markers to be an image
//$sp->mark->SetType(MARK_IMG_PUSHPIN,'blue',0.8);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
// Install the Y-X callback for the markers
$sp->mark->SetCallbackYX('FCallback');
// ...  and add it to the graph
$textcolor='deepskyblue3';
$graph->Add($sp);
$txt0 = new Text("$wastedresult[0]".'%');
$txt0->SetFont(FF_ARIAL,FS_BOLD,26);
$txt0->SetPos(185,260);
$txt0->SetColor($textcolor);
$txt1 = new Text("$wastedresult[1]".'%');
$txt1->SetFont(FF_ARIAL,FS_BOLD,26);
$txt1->SetPos(185,825);
$txt1->SetColor($textcolor);
$txt2 = new Text("$wastedresult[2]".'%');
$txt2->SetFont(FF_ARIAL,FS_BOLD,26);
$txt2->SetPos(570,260);
$txt2->SetColor($textcolor);
$txt3 = new Text("$wastedresult[3]".'%');
$txt3->SetFont(FF_ARIAL,FS_BOLD,26);
$txt3->SetPos(570,825);
$txt3->SetColor($textcolor);
$txt4 = new Text("$wastedresult[4]".'%');
$txt4->SetFont(FF_ARIAL,FS_BOLD,26);
$txt4->SetPos(1010,260);
$txt4->SetColor($textcolor);
$txt5 = new Text("$wastedresult[5]".'%');
$txt5->SetFont(FF_ARIAL,FS_BOLD,26);
$txt5->SetPos(1010,825);
$txt5->SetColor($textcolor);
$txt6 = new Text("$wastedresult[6]".'%');
$txt6->SetFont(FF_ARIAL,FS_BOLD,26);
$txt6->SetPos(1370,260);
$txt6->SetColor($textcolor);
$txt7 = new Text("$wastedresult[7]".'%');
$txt7->SetFont(FF_ARIAL,FS_BOLD,26);
$txt7->SetPos(1370,825);
$txt7->SetColor($textcolor);
$bottomtext =new Text("Wasted energy ratio is percentage of electrical energy \nused by air conditioning system when users are not in the area.");
$bottomtext->SetFont(FF_ARIAL,FS_BOLD,32);
$bottomtext->SetPos(50,1170);
$bottomtext->SetColor('black');
$bottomtext->SetBox('white','black');

//$txt->SetBox('yellow','black');
//$txt->SetShadow();
$graph->AddText($txt0);
$graph->AddText($txt1);
$graph->AddText($txt2);
$graph->AddText($txt3);
$graph->AddText($txt4);
$graph->AddText($txt5);
$graph->AddText($txt6);
$graph->AddText($txt7);
$graph->AddText($bottomtext);

$picpath='/var/www/html/';
$picname='fl13wasted_lab.png';
$graph->Stroke($picname);
//$graph->Stroke();
//$uploaddropbox = shell_exec('/var/www/html/uploaddropbox.sh');
uploaddropbox($picname);
function uploaddropbox($picname){
$url = "https://content.dropboxapi.com/2/files/upload";
$headers = array(
        "Authorization: Bearer wHfYxEh5FNYAAAAAAAAD3LPVcxwEMKzKqLu4ncfagRFkiwUOgU-UizhZOXyKImPS",
        "Content-Type: application/octet-stream",
        "Dropbox-API-Arg: {\"path\": \"/CU_EE_fl13/EE_information/$picname\",\"mode\": \"overwrite\",\"autorename\": false,\"mute\": false}");
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POST, true);
        $file = $picname;
        $fp = fopen($file, 'rb');
        curl_setopt($ch, CURLOPT_POSTFIELDS,fread($fp,filesize($file)));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        fclose($fp);
        echo $response;
}
function checkvalue($value1){
        if(is_numeric($value1)){
                return number_format(round($value1,1),1,'.','');
        }else{
                return "NaN";
        }
}
function fetchdata($keyid,$uuid){
$mydata=
"<?xml version='1.0' encoding='UTF-8'?>
<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/'>
<soapenv:Body>
<ns2:queryRQ xmlns:ns2='http://soap.fiap.org/'>
<transport xmlns='http://gutp.jp/fiap/2009/11/'>
<header>
<query id='".$uuid."' type='storage'>
<key id='$keyid' attrName='time' select='maximum' />
</query>
</header>
</transport>
</ns2:queryRQ>
</soapenv:Body>
</soapenv:Envelope>";
$url = "http://161.200.90.122/axis2/services/FIAPStorage";
 $headers = array(
    "Content-type: text/xml"
    ,"Content-length: ".strlen($mydata)
    ,"SOAPAction: http://soap.fiap.org/query"
    );
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt ($ch, CURLOPT_SSL_VERIFYHOST, 0);
            curl_setopt ($ch, CURLOPT_SSL_VERIFYPEER, 0);
            curl_setopt($ch, CURLOPT_POSTFIELDS,  $mydata);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
            curl_setopt($ch, CURLOPT_VERBOSE, 0);
            $data = curl_exec($ch);
            if($data === false){
                $error = curl_error($ch);
                echo $error;
                die('error occured');
            }else{
                                $xml = simplexml_load_string($data);
                                $ns = $xml->getNamespaces(true);
                                 $child =(string)
                                $xml->children($ns['soapenv'])->
                                Body->children($ns['ns2'])->
                                queryRS->children($ns[''])->transport->body->point->value;
                                $para[1]=$child;
                                $child2 =(string)
                                $xml->children($ns['soapenv'])->
                                Body->children($ns['ns2'])->
                                queryRS->children($ns[''])->transport->body->point->value->attributes();
                                $para[2]=$child2;
            }
            curl_close($ch);
                        return $para;
}
function uuid(){
  return sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
    mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff), mt_rand( 0, 0xffff ),
    mt_rand( 0, 0x0fff ) | 0x4000,
    mt_rand( 0, 0x3fff ) | 0x8000,
    mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff), mt_rand( 0, 0xffff ));
}
function checkdate1($data,$yest){
        $datats=explode("T",$data[2]);
        if($datats[0] == $yest){
                return $data[1];
        }else{
                return "NaN";
        }

}
function colorresult($valuea){
        if(!is_numeric($valuea)){
                return $result="black";
        }else{
        if ($valuea == 0){
                $result="chartreuse4";
        }elseif($valuea > 0 && $valuea < 10){
                $result="chartreuse3";
        }elseif ($valuea >= 10 && $valuea < 20){
                $result="chartreuse2";
        }elseif ($valuea >= 20 && $valuea < 30){
                $result="chartreuse1";
        }elseif ($valuea >= 30 && $valuea < 40){
                $result="yellow";
        }elseif ($valuea >= 40 && $valuea < 50){
                $result="yellow2";
        }elseif ($valuea >= 50 && $valuea < 60){
                $result="orange";
        }elseif ($valuea >= 60 && $valuea < 70){
                $result="orange3";
        }elseif ($valuea >= 70 && $valuea < 80){
                $result="tomato";
        }elseif ($valuea >= 80 && $valuea <90){
                $result="orangered2";
        }elseif ($valuea >=90 && $valuea < 100){
                $result="red";
        }elseif ($valuea==100){
                $result="darkred";
        }else{
                $result="black";
                }
        }
        return $result;
}
?>
