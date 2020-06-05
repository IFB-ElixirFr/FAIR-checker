
$(document).ready(function(){
    // Client Side Javascript to receive numbers.
    // // start up the SocketIO connection to the server - the namespace 'test' is also included here if necessary
    // var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // // this is a callback that triggers when the "my response" event is emitted by the server.
    // socket.on('my response', function(msg) {
    //     $('#log').append('<p>Received: ' + msg.data + '</p>');
    // });
    // //example of triggering an event on click of a form submit button
    // $('form#emit').submit(function(event) {
    //     socket.emit('my event', {data: $('#emit_data').val()});
    //     return false;
    // });

    var table = $('#summary_table').DataTable({
        "aaSorting": [],
        "columns": [
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
            null,
            null,
            null,
        ],
        // "responsive": {
        //     "details": {
        //         "type": 'column'
        //     }
        // },
        // "columnDefs": [ {
        //     "className": 'control',
        //     "orderable": false,
        //     "targets":   0
        // } ],
    });

    function format ( value ) {
        // console.log(value);
        // var json = JSON.parse(value);
        // `d` is the original data object for the row
        // return '<div>Hidden Value: ' + value.descriptions + '</div>';
        return '<table class="box" cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
            '<tr>'+
                '<td>Description:</td>'+
                '<td>'+value.descriptions+'</td>'+
            '</tr>'+
            '<tr>'+
                '<td>Comments:</td>'+
                '<td>'+value.comments+'</td>'+
            '</tr>'+
        '</table>';
    }

    // Add event listener for opening and closing details
    $('#summary_table').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(format(tr.data('child-value'))).show();
            tr.addClass('shown');
        }
    } );

});
