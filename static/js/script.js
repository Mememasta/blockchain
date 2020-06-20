function timestampToDate(ts) {

    var d = new Date();
    d.setTime(ts * 1000);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; 
    return ('0' + d.getDate()).slice(-2) + ' ' + months[d.getMonth()] + ' ' + d.getFullYear() + ' ' + d.getHours() + ':' + ('0' + d.getMinutes()).slice(-2);
}

