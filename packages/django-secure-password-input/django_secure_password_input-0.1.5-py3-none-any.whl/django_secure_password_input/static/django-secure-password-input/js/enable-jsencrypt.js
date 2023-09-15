;!(function($){
    $(document).ready(function(){
        $(".django-secure-password-input").parents("form").submit(function(){
            var form = $(this);
            form.find(".django-secure-password-input").each(function(index, widget){
                var public_key = $(this).attr("public_key");
                var value = $(this).val();
                var encrypt = new JSEncrypt();
                encrypt.setPublicKey(public_key);
                var encrypted_value = encrypt.encrypt(value);
                $(this).attr("plain_value", value);
                $(this).val("rsa-encrypted:" + encrypted_value);
            });

        });
    });
})(jQuery);
