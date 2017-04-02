<?php
require_once ('/var/www/html/jpgraph/src/jpgraph.php');
require_once ('/var/www/html/jpgraph/src/jpgraph_scatter.php');
$now1=date("Y-m-d H:i:s");
$yest=date('Y-m-d',strtotime("-1 days"));
DEFINE('fl13lecturer','/var/www/html/fl13_lecturer.png');
$zonefl13[0]='http://khetnon/eng4/fl13/south/room_csc_jpl_ccr/z1/analytic/wasted_energy/per_day';
$zonefl13[1]='http://khetnon/eng4/fl13/south/room_pkp_pjp_was/z1/analytic/wasted_energy/per_day';
$zonefl13[2]='http://khetnon/eng4/fl13/south/room_cak_cpp_lwk/z1/analytic/wasted_energy/per_day';
$zonefl13[3]='http://khetnon/eng4/fl13/south/room_sav_dwc_nts/z1/analytic/wasted_energy/per_day';
$zonefl13[4]='http://khetnon/eng4/fl13/south/lectureroom_2/z1/analytic/wasted_energy/per_day';
$zonefl13[5]='http://khetnon/eng4/fl13/south/lectureroom_dsp/z1/analytic/wasted_energy/per_day';
$uuid=uuid();
foreach ($zonefl13 as &$key){
        //$wastedresult[]=number_format(round(fetchdata($key,$uuid),1),1,'.','');
        $wastedresult[]=checkvalue(checkdate1(fetchdata($key,$uuid),$yest));
}
//var_dump($wastedresult);
foreach ($wastedresult as &$key1){
        $colorresult[]=colorresult($key1);
}
$data = array(
    array(9,68,66,$colorresult[0]),
    array(24,68,66,$colorresult[1]),
    array(43,68,66,$colorresult[2]),
    array(60,68,66,$colorresult[3]),
        array(73,68,66,$colorresult[4]),
        array(88,68,66,$colorresult[5])
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
$graph->SetBackgroundImage(fl13lecturer,BGIMG_FILLPLOT);

// Setup a nice title with a striped bevel background
$graph->title->Set("Floor 13 lecturer room:  Wasted energy ratio (daily update)                 Modified:$now1");
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
$colorfont='white';
$graph->Add($sp);
$txt0 = new Text("$wastedresult[0]".'%');
$txt0->SetFont(FF_ARIAL,FS_BOLD,31);
$txt0->SetPos(120,425);
$txt0->SetColor($colorfont);
$txt1 = new Text("$wastedresult[1]".'%');
$txt1->SetFont(FF_ARIAL,FS_BOLD,31);
$txt1->SetPos(410,425);
$txt1->SetColor($colorfont);
$txt2 = new Text("$wastedresult[2]".'%');
$txt2->SetFont(FF_ARIAL,FS_BOLD,31);
$txt2->SetPos(770,425);
$txt2->SetColor($colorfont);
$txt3 = new Text("$wastedresult[3]".'%');
$txt3->SetFont(FF_ARIAL,FS_BOLD,31);
$txt3->SetPos(1110,425);
$txt3->SetColor($colorfont);
$txt4 = new Text("$wastedresult[4]".'%');
$txt4->SetFont(FF_ARIAL,FS_BOLD,31);
$txt4->SetPos(1340,425);
$txt4->SetColor($colorfont);
$txt5 = new Text("$wastedresult[5]".'%');
$txt5->SetFont(FF_ARIAL,FS_BOLD,31);
$txt5->SetPos(1640,425);
$txt5->SetColor($colorfont);
$bottomtext =new Text("Wasted energy ratio is percentage of electrical energy \nused by air conditioning system when users are not in the area.");
$bottomtext->SetFont(FF_ARIAL,FS_BOLD,36);
$bottomtext->SetPos(30,1130);
$bottomtext->SetColor('black');
//$bottomtext->SetBox('white','white');
//$txt->SetBox('yellow','black');
//$txt->SetShadow();
$graph->AddText($txt0);
$graph->AddText($txt1);
$graph->AddText($txt2);
$graph->AddText($txt3);
$graph->AddText($txt4);
$graph->AddText($txt5);
$graph->AddText($bottomtext);

// .. and output to browser
$graph->Stroke('/var/www/html/fl13wasted_lecturer.png');
//$graph->Stroke();
$uploaddropbox = shell_exec('/var/www/html/uploaddropbox.sh fl13wasted_lecturer.png');
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
function checkvalue($value1){
        if(is_numeric($value1)){
                return number_format(round($value1,1),1,'.','');
        }else{
                return "NaN";
        }
}
function checkdate1($data,$yest){
        $datats=explode("T",$data[2]);
        if($datats[0] == $yest){
                return $data[1];
        }else{
                return "NaN";
        }

}
?>
