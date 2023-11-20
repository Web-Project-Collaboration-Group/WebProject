    function $(id)
    {
        return document.getElementById(id);
    }
    function delete1()
    {
        alert('删除成功！');
    }
    function del_s()
    {
        var ids = document.getElementsByName("choose_s")
        var str = [];
        for(i=0;i<ids.length;i++)
        {
            if(ids[i].checked)
            {
                str.push(ids[i].value);
            }
        }
        if(str!='')
        {
            $("del_chosen").href = "/del_s?id=" + str;
            alert('批量删除成功！');
        }
        else
        {
            alert('请选择批量删除对象！');
        }
    }
    function update_s()
    {
        var ids = document.getElementsByName("choose_s")
        var str = [];
        for(i=0;i<ids.length;i++)
        {
            if(ids[i].checked)
            {
                str.push(ids[i].value);
            }
        }
        if(str!='')
        {
            $("update_chosen").href = "/update_s?id=" + str;
        }
        else
        {
            alert('请选择批量修改对象！');
        }
    }