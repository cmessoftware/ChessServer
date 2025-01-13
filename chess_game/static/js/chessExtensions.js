// import Chess, { prototype } from 'chess.js';

// // Add a custom method to the Chess prototype
// prototype.isPawnPromotionPossible = function (color) {
//     const rank = color === 'w' ? '7' : '2';
//     const board = this.board();

//     for (let file = 0; file < 8; file++) {
//         const square = board[rank][file];
//         if (square && square.type === 'p' && square.color === color) {
//             return true; // Pawn is ready for promotion
//         }
//     }
//     return false;
// };

// // Add a custom method to the Chess prototype
// prototype.isGameOver = function () {
//     return this.game_over();
// };  

// export default Chess;