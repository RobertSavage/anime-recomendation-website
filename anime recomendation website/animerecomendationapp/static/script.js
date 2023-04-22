var closed_big = document.querySelectorAll('.closed_big')

anime({
    targets: closed_big,
    loop: true,
    delay: 0,
    scaleX: 0.9,
	scaleY: 0.9,
	direction: 'alternate',
    easing: 'easeInOutSine'
});

var open2 = document.querySelectorAll('.open2')

anime({
    targets: open2,
    loop: true,
    delay: 20,
    scaleX: 0.9,
	scaleY: 0.9,
	direction: 'alternate',
    easing: 'easeInOutSine'
});


var big_dash = document.querySelectorAll('.big_dash')

anime({
    targets: big_dash,
    loop: true,
    delay: 0,
    rotate: 360,
    direction: 'reverse',
    duration: 20000,
    easing: 'easeInOutSine'
});


var small_dash = document.querySelectorAll('.small_dash')

anime({
    targets: small_dash,
    loop: true,
    delay: 0,
    rotate: 360,
    direction: 'reverse',
    duration: 20000,
    easing: 'easeInOutSine'
});
