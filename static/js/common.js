function CheckKeyword(key) {
    const layer = layui.layer;
    if (key === 'search') {
        const keyword = document.getElementById("search_keyword").value;
        if (keyword.length < 1) {
            layer.alert('查询内容不能为空！', {
                title: '查询失败！'
            })
            return false;
        } else {
            return true;
        }
    }
}