# Copyright (C) 2023, NG:ITL
import typing
import datetime
import os
import uuid

from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID


FILE_DIR = Path(__file__).parent


def private_key_generate() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())


def private_key_load(private_key_filepath: Path, password: str) -> rsa.RSAPrivateKey:
    with open(private_key_filepath, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password.encode("utf-8"), default_backend())
        assert isinstance(private_key, rsa.RSAPrivateKey)
        return private_key


def private_key_save(private_key_filepath: Path, key: rsa.RSAPrivateKey, password: str) -> None:
    with open(private_key_filepath, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
            )
        )


def certificate_create(key: rsa.RSAPrivateKey) -> x509.Certificate:
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "CA"),
        ]
    )
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            # Our certificate will be valid for 10 years
            datetime.datetime.utcnow()
            + datetime.timedelta(days=10 * 365)
        )
        .add_extension(
            x509.BasicConstraints(
                ca=True,
                path_length=None,  # pathlen: is equal to the number of CAs/ICAs it can sign
            ),
            critical=True,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,  # nonRepudiation
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
                # ca
                key_cert_sign=True,
                crl_sign=True,
            ),
            critical=True,
        )
        .sign(
            # Sign our certificate with our private key
            key,
            hashes.SHA256(),
            default_backend(),
        )
    )


def certificate_load(certificate_filepath: Path) -> x509.Certificate:
    with open(certificate_filepath, "rb") as f:
        return x509.load_pem_x509_certificate(f.read(), default_backend())


def certificate_save(certificate_filepath: Path, data: x509.Certificate) -> None:
    with open(certificate_filepath, "wb") as f:
        f.write(data.public_bytes(serialization.Encoding.PEM))
    with open(f"{certificate_filepath}.cer", "wb") as f:
        f.write(data.public_bytes(serialization.Encoding.DER))
    cwd = os.getcwd()
    os.chdir(certificate_filepath.parent)
    os.symlink(certificate_filepath, str(data.serial_number))
    os.chdir(cwd)


def certificate_signing_request_create(
    email: str,
    key: rsa.RSAPrivateKey,
    country: typing.Union[str, None] = None,
    state: typing.Union[str, None] = None,
    locality: typing.Union[str, None] = None,
    organization: typing.Union[str, None] = None,
    commonname: typing.Union[str, None] = None,
) -> x509.CertificateSigningRequest:
    names = []
    for t, v in (
        (NameOID.COUNTRY_NAME, country),
        (NameOID.STATE_OR_PROVINCE_NAME, state),
        (NameOID.LOCALITY_NAME, locality),
        (NameOID.ORGANIZATION_NAME, organization),
        (NameOID.COMMON_NAME, commonname),
    ):
        if v:
            names.append(x509.NameAttribute(t, v))
    names.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, email))
    return (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name(names))
        .sign(
            # Sign the CSR with our private key.
            key,
            hashes.SHA256(),
            default_backend(),
        )
    )


def certificate_signing_request_load(certificate_signing_request_filepath: Path) -> x509.CertificateSigningRequest:
    with open(certificate_signing_request_filepath, "rb") as f:
        return x509.load_pem_x509_csr(data=f.read(), backend=default_backend())


def public_key_save(public_key_filepath: Path, private_key: rsa.RSAPrivateKey) -> None:
    with open(public_key_filepath, "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )


def pk12_save(
    name: bytes,
    cert: x509.Certificate,
    key: rsa.RSAPrivateKey,
    central_authority: "CentralAuthority",
    pk12_filepath: Path,
    password: str,
) -> None:
    data = pkcs12.serialize_key_and_certificates(
        name=name,
        key=key,
        cert=cert,
        cas=[central_authority.certificate],
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf8")),
    )
    with open(pk12_filepath, "wb") as f:
        f.write(data)


def pk12_load(pk12_filepath: Path, password: str) -> pkcs12.PKCS12KeyAndCertificates:
    with open(pk12_filepath, "rb") as fp:
        pk12 = pkcs12.load_key_and_certificates(fp.read(), password.encode("utf-8"), default_backend())
        assert isinstance(pk12, pkcs12.PKCS12KeyAndCertificates)
        return pk12


class CentralAuthority:
    def __init__(self, private_key_filepath: Path, certificate_filepath: Path, password: str) -> None:
        if private_key_filepath.exists():
            self.private_key = private_key_load(private_key_filepath, password)
        else:
            self.private_key = private_key_generate()
            private_key_save(private_key_filepath, self.private_key, password)

        if certificate_filepath.exists():
            self.certificate = certificate_load(certificate_filepath)
        else:
            self.certificate = certificate_create(self.private_key)
            certificate_save(certificate_filepath, self.certificate)

    def sign_certificate_signing_request(self, csr: x509.CertificateSigningRequest) -> x509.Certificate:
        emails = csr.subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)
        assert isinstance(emails[0].value, str)
        names = [x509.RFC822Name(emails[0].value)]
        return (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(self.certificate.subject)
            .public_key(csr.public_key())
            .serial_number(uuid.uuid4().int)  # pylint: disable=no-member
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(self.private_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.CRLDistributionPoints(
                    [
                        x509.DistributionPoint(
                            full_name=[x509.UniformResourceIdentifier("http://ca.trisoft.com.pl/crl")],
                            relative_name=None,
                            reasons=None,
                            crl_issuer=None,
                        )
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.AuthorityInformationAccess(
                    [
                        x509.AccessDescription(
                            x509.OID_CA_ISSUERS,
                            x509.UniformResourceIdentifier("http://ca.trisoft.com.pl/cacert"),
                        ),
                        x509.AccessDescription(
                            x509.OID_OCSP,
                            x509.UniformResourceIdentifier("http://ca.trisoft.com.pl/ocsp"),
                        ),
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.SubjectAlternativeName(names),
                critical=False,
            )
            # certificate_policies
            .add_extension(
                x509.ExtendedKeyUsage([x509.OID_CLIENT_AUTH, x509.OID_EMAIL_PROTECTION]),
                critical=False,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(csr.public_key()),
                critical=False,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=True,  # nonRepudiation
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=True,
                    encipher_only=False,
                    decipher_only=False,
                    # ca
                    key_cert_sign=False,
                    crl_sign=False,
                ),
                critical=True,
            )
            .sign(
                private_key=self.private_key,
                algorithm=hashes.SHA256(),
                backend=default_backend(),
            )
        )


def identity_create(
    output_dirpath: Path, name: str, private_key_password: str, central_authority: CentralAuthority
) -> None:
    identity_dirpath = output_dirpath / name
    identity_dirpath.mkdir(exist_ok=True)

    certificate_filepath = identity_dirpath / f"{name}.crt.pem"
    private_key_filepath = identity_dirpath / f"{name}.priv.pem"
    public_key_filepath = identity_dirpath / f"{name}.pub.pem"
    p12_filepath = identity_dirpath / f"{name}.p12"

    client_pk = private_key_generate()
    client_csr = certificate_signing_request_create(name, client_pk)
    client_cert = central_authority.sign_certificate_signing_request(client_csr)

    certificate_save(certificate_filepath, client_cert)
    private_key_save(private_key_filepath, client_pk, private_key_password)
    public_key_save(public_key_filepath, client_pk)
    pk12_save(
        "USER cert".encode("utf-8"), client_cert, client_pk, central_authority, p12_filepath, private_key_password
    )
