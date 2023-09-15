use proc_macro::TokenStream;
use quote::quote;
use syn::{self, Data};

#[proc_macro_derive(IntoPy)]
pub fn into_py_macro_derive(input: TokenStream) -> TokenStream {
    let ast = syn::parse(input).unwrap();
    impl_into_py_macro(&ast)
}

fn impl_into_py_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let data: &Data = &ast.data;
    match data {
        Data::Enum(data_enum) => {
            let match_arms = data_enum.variants.iter().map(|variant| {
                let variant_ident = &variant.ident;
                quote! {
                    #name::#variant_ident(x) => x.into_py(py),
                }
            });

            quote! {
            impl IntoPy<PyObject> for #name {
                fn into_py(self, py: Python<'_>) -> PyObject {
                    match self {
                        #(#match_arms)*
                    }
                }
            }}
            .into()
        }
        _ => panic!("Can only derive for Enum"),
    }
}
