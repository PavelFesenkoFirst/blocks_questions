function showOrderUp(){
    console.log('work');

    $.ajax('/api/v1/block/up')
        .done(data => {
            console.log(data);
            $('#blocks').html(``);
            for (let item of data){
                console.log(item);
                $('#blocks').append(`
                <div class="my-3 p-3 bg-white rounded shadow-sm">
                    <h2 class="border-bottom border-dark pb-2 mb-0">${item.title}</h2>
                    <div class="row text-muted pt-3">
                        <p class="media-body pb-3 mb-0 pl-3 small border-dark">
                            Данный блок сожерит ${item.questions} вопросов
                        </p>
                        <p class="media-body pb-3 mb-0 small border-dark">
                            ${item.description}
                        </p>
                        <a class="btn btn-secondary m-2" href="${item.link}">Подробнее...</a>
                    </div>
                </div>
                `)
            }
        })
}


function showOrderDown(){
    console.log('work');

    $.ajax('/api/v1/block/down')
        .done(data => {
            console.log(data);
            $('#blocks').html(``);
            for (let item of data){
                console.log(item);
                $('#blocks').append(`
                <div class="my-3 p-3 bg-white rounded shadow-sm">
                    <h2 class="border-bottom border-dark pb-2 mb-0">${item.title}</h2>
                    <div class="row text-muted pt-3">
                        <p class="media-body pb-3 mb-0 pl-3 small border-dark">
                            Данный блок сожерит ${item.questions} вопросов
                        </p>
                        <p class="media-body pb-3 mb-0 small border-dark">
                            ${item.description}
                        </p>
                        <a class="btn btn-secondary m-2" href="${item.link}">Подробнее...</a>
                    </div>
                </div>
                `)
            }
        })
}

function showFilter(){
    console.log('work');

    $.ajax('/api/v1/block/filter')
        .done(data => {
            console.log(data);
            $('#blocks').html(``);
            for (let item of data){
                console.log(item);
                $('#blocks').append(`
                <div class="my-3 p-3 bg-white rounded shadow-sm">
                    <h2 class="border-bottom border-dark pb-2 mb-0">${item.title}</h2>
                    <div class="row text-muted pt-3">
                        <p class="media-body pb-3 mb-0 pl-3 small border-dark">
                            Данный блок сожерит ${item.questions} вопросов
                        </p>
                        <p class="media-body pb-3 mb-0 small border-dark">
                            ${item.description}
                        </p>
                        <a class="btn btn-secondary m-2" href="${item.link}">Подробнее...</a>
                    </div>
                </div>
                `)
            }
        })
}
