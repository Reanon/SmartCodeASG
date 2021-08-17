/*
 * @source: https://ethernaut.zeppelin.solutions/level/0xf70706db003e94cfe4b5e27ffd891d5c81b39488
 * @author: Alejandro Santander
 * @vulnerable_at_lines: 24
 */

pragma solidity ^0.4.18;

contract Reentrance {
    mapping(address => uint) public balances;

    function withdraw(uint _amount) public {
        msg.sender.call.value(_amount)();

        balances[msg.sender] -= _amount;
    }
    function call() public {
        withdraw(1);
    }

    function call2() public {

    }
    function call3() public {

    }
    function() public payable {}
}
