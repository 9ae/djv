/**
 * Created by ari on 6/18/14.
 */


function updateBar(percent){
	$('#uploadProgress').attr('aria-valuenow', percent);
	$('#uploadProgress').css('width',percent+'%');
}

function uploadFile(event){
    var token = $('#uploadTokenId').val();
    if(token==""){
        return;
    }
    var url = makeURL('uploadToken','upload');

    var data = new FormData($('#upload')[0]); // <-- 'this' is your form element
    console.log(data);
    updateBar(20);
    $.ajax({
            url: url,
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            type: 'POST',
            success: function(data) {
                console.log('upload to token');
                var uploadResults = data;
                console.log(uploadResults);
                if (uploadResults['fileName'] != undefined) {
                    var fileName = uploadResults['fileName'];
                    $.post(makeURL('media', 'add'), {'entry:mediaType': 1, 'entry:name':fileName }, function (data) {
                        console.log('create media');
                        var addMediaResults = data;
                        console.log(addMediaResults);
                        var linkBody = {'entryId': addMediaResults.id,
                            'resource:token': token,
                            'resource:objectType': 'KalturaUploadedFileTokenResource'};
                        $.post(makeURL('media', 'addContent'), linkBody, function (data) {
                            console.log('upload complete');
                            console.log(data);
                            var entryResults = data;
                            var thinkBody = {'id': entryResults.id, 'services':{'stockpodium':true,'voicebase':true}};
                            thinkBody = JSON.stringify(thinkBody);
                            $.ajax({
                                url:'/media/',
                                type: 'POST',
                                contentType:'application/json',
                                data: thinkBody
                            }).done(function(){
                                console.log('sent for tagging');
                                updateBar(100);
                            });
                        }).done(function(){  updateBar(80); }); // end of addcontent
                    }).done(function(){  updateBar(60); }); // end of add media
                } //end of if
            }
    }).done(function(){  updateBar(40); }); // end of upload
}

$('#do_upload').click(uploadFile);
