// function modalOpen() {
//     document.querySelector('.window').style.display = 'block';
//     document.querySelector('.background').style.display = 'block';
// }

// // 모달 끄기
// function modalClose() {
//     document.querySelector('.window').style.display = 'none';
//     document.querySelector('.background').style.display = 'none';
// }

// //버튼 클릭리스너 달기
// document.querySelector('#show').addEventListener('click', modalOpen);
// document.querySelector('#close').addEventListener('click', modalClose);

// // ready 부분 -> reload 부분
// $(document).ready(function () {

// });

// //후기를 작성하면 서버로 내용을 보내서 저장하는 함수
// function comment() {
//     console.log("여기까지는 나오는가")
//     let comment = document.getElementById('comment').value;
//     let userID = document.getElementById('userID').value;
//     let today = new Date().toISOString();
//     // 이름을 어떻게 가져올것인가?
//     // let name =
//     console.log(comment);
//     console.log(today);

//     $.ajax({
//         type: "POST",
//         url: "/api/single/post_comment",
//         data: {
//             comment_give: comment,
//             date_give: today,
//             userID_give: userID
//         },
//         success: function (response) {
//             if(response["result"] == "success"){
//                 alert(response["msg"]);
//             $("#comment-box").removeClass("is-active");
//             window.location.reload();
//             }
//         }
//     });
// }

