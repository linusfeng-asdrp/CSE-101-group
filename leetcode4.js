var reverseList = function(head) {
    let prev = null;
    let curr = head;

    while (curr !== null) {
        let nextTemp = curr.next; // store the next node
        curr.next = prev;         // reverse the pointer
        prev = curr;              // move prev forward
        curr = nextTemp;          // move curr forward
    }

    return prev; // new head of the reversed list
};
