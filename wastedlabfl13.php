<?php 
require_once ('./jpgraph/src/jpgraph.php');
require_once ('./jpgraph/src/jpgraph_scatter.php');
$now1=date("Y-m-d H:i:s"); 
DEFINE('fl13','./fl13_lab.png');
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
        $wastedresult[]=fetchdata($key,$uuid);
}
//var_dump($wastedresult);
 foreach ($wastedresult as &$key1){
        $colorresult[]=colorresult($key1);
}
//var_dump($colorresult);



function markCallback($y,$x) {
    // Return array width
    // width,color,fill color, marker filename, imgscale
    // any value can be false, in that case the default value will
    // be used.
    // We only make one pushpin another color
    if( $x == 54 ) 
    return array(false,false,false,'red',0.8);
    else
    return array(false,false,false,'yellow',2);
}
 
// Data arrays
//$datax = array(10,20,30,40,54,60,70,80);
//$datay = array(15,23,65,18,84,28,86,44);
 
$data = array(
    array(18,82,40,$colorresult[0]),
    array(17,34,40,$colorresult[1]),
    array(36,82,40,$colorresult[2]),
    array(37,34,40,$colorresult[3]),
	array(54,82,40,$colorresult[4]),
	array(54,34,40,$colorresult[5]),
	array(73,82,40,$colorresult[6]),
	array(73,34,40,$colorresult[7])


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
// Callback for markers
// Must return array(width,border_color,fill_color,filename,imgscale)
// If any of the returned values are '' then the
// default value for that parameter will be used (possible empty)
function FCallback($aYVal,$aXVal) {
    global $format;
    return array($format[strval($aXVal)][strval($aYVal)][0],'',
         $format[strval($aXVal)][strval($aYVal)][1],'','');
}
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
$graph->title->Set("             Floor 13 research lab:  Wasted energy ratio         Modified:$now1");
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
$graph->Add($sp);    
 
// .. and output to browser
$graph->Stroke('/var/www/html/wastefl13.png');
//$graph->Stroke();
$uploaddropbox = shell_exec('/var/www/html/uploaddropbox.sh');




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
                                $para=$child;
                                $child2 =(string)
                                $xml->children($ns['soapenv'])->
                                Body->children($ns['ns2'])->
                                queryRS->children($ns[''])->transport->body->point->value->attributes();
                                //$para[2]=$child2;
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

function colorresult($value){
        if ($value =0){
                $result="chartreuse4";
        }elseif ($value<=9){
                $result="chartreuse3";
		}elseif ($value<=19){
                $result="chartreuse2";
		}elseif ($value<=29){
                $result="chartreuse1";
		}elseif ($value<=39){
                $result="yellow";
        }elseif ($value<=49){
                $result="yellow2";
		}elseif ($value<=59){
                $result="orange";
		}elseif ($value<=69){
                $result="orange3";
		}elseif ($value<=79){
                $result="tomato";
		}elseif ($value<=89){
                $result="orangered2";
        }elseif ($value<=99){
                $result="red";
        }elseif ($value=100){
                $result="darkred";
        }else{
                $result="black";
        }
        return $result;

}

?>
