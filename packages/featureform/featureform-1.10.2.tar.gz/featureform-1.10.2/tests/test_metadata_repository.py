import os
import shutil
import stat
from dataclasses import replace

from featureform import SQLiteMetadata, FeatureVariant, ScalarType
from featureform.metadata_repository import (
    MetadataRepository,
    MetadataRepositoryLocalImpl,
)

import pytest

from featureform.resources import (
    ResourceLocation,
    Feature,
    User,
    LabelVariant,
    Provider,
    EmptyConfig,
    SourceVariant,
    PrimaryData,
    SQLTable,
    Label,
    Model,
    Entity,
    TrainingSetVariant,
    TrainingSet,
)

test_user = User(name="test_user", tags=["tag1"], properties={"key1": "value1"})

model = Model(name="model")

entity = Entity(name="entity", description="fake description")

provider = Provider(
    name="provider",
    description="fake description",
    team="fake_team",
    config=EmptyConfig(),
    function="",
    status="ready",  # look into this
)

resource_location = ResourceLocation(
    entity="Dummy Entity", value="Dummy Value", timestamp="12345"
)
feature_variant = FeatureVariant(
    name="feature",
    source=("source", "variant1"),
    value_type=ScalarType.FLOAT32.value,
    entity="fake_entity",
    owner="fake_owner",
    provider="fake_provider",
    location=resource_location,
    description="fake description",
    variant="variant1",
    is_embedding=False,
    dims=0,
    tags=["tag1"],
    properties={"key1": "value1"},
)

source_variant = SourceVariant(
    name="source",
    variant="variant1",
    definition=PrimaryData(location=SQLTable(name="")),
    owner="fake_owner",
    provider="fake_provider",
    description="fake description",
    tags=[],
    properties={},
)

label_variant = LabelVariant(
    name="label",
    source=("source", "variant1"),
    value_type=ScalarType.FLOAT32.value,
    entity="fake_entity",
    owner="fake_owner",
    provider="fake_provider",
    location=resource_location,
    description="fake description",
    variant="variant1",
    tags=["tag1"],
    properties={"key1": "value1"},
)

training_set_variant = TrainingSetVariant(
    name="training_set",
    owner="fake_owner",
    label=("label", "variant1"),
    features=[("feature", "variant1")],
    description="fake description",
    variant="variant1",
    tags=["tag1"],
    properties={"key1": "value1"},
    status="ready",
)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    shutil.rmtree(".featureform", onerror=del_rw)


def del_rw(action, name, exc):
    if os.path.exists(name):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)


@pytest.fixture(scope="function")
def setup() -> MetadataRepository:
    with SQLiteMetadata() as db:
        yield MetadataRepositoryLocalImpl(db)


@pytest.mark.local
def test_create_model(setup):
    repo = setup
    repo.create_resource(model)
    assert repo.get_model("model") == model


@pytest.mark.local
def test_get_models(setup):
    repo = setup
    repo.create_resource(model)
    model2 = replace(model, name="fake_model2")
    repo.create_resource(model2)

    models = repo.get_models()
    assert len(models) == 2  # there's one more for local mode
    assert model in models
    assert model2 in models


@pytest.mark.local
def test_create_entity(setup):
    repo = setup
    repo.create_resource(entity)
    assert repo.get_entity("entity") == entity


@pytest.mark.local
def test_get_entities(setup):
    repo = setup
    repo.create_resource(entity)
    entity2 = replace(entity, name="entity2")
    repo.create_resource(entity2)

    entities = repo.get_entities()
    assert len(entities) == 2  # there's one more for local mode
    assert entity in entities
    assert entity2 in entities


@pytest.mark.local
def test_create_provider(setup):
    repo = setup
    repo.create_resource(provider)
    assert repo.get_provider("provider") == provider


@pytest.mark.local
def test_get_providers(setup):
    repo = setup
    repo.create_resource(provider)
    provider2 = replace(provider, name="fake_provider2")
    repo.create_resource(provider2)

    providers = repo.get_providers()
    assert len(providers) == 2  # there's one more for local mode
    assert provider in providers
    assert provider2 in providers


@pytest.mark.local
def test_create_source_variant(setup):
    repo = setup
    repo.create_resource(source_variant)
    assert repo.get_source_variant("source", "variant1") == source_variant


@pytest.mark.local
def test_get_sources(setup):
    repo = setup
    repo.create_resource(source_variant)
    source2 = replace(source_variant, variant="variant2")
    repo.create_resource(source2)

    sources = repo.get_sources()
    assert len(sources) == 1
    assert sources[0].variants == ["variant1", "variant2"]


@pytest.mark.local
def test_create_label_variant(setup):
    repo = setup
    repo.create_resource(label_variant)
    assert repo.get_label_variant("label", "variant1") == label_variant


@pytest.mark.local
def test_get_labels(setup):
    repo = setup
    repo.create_resource(label_variant)
    label_variant2 = replace(label_variant, variant="variant2")
    repo.create_resource(label_variant2)

    labels = repo.get_labels()
    assert len(labels) == 1
    assert labels[0] == Label(
        name="label",
        default_variant="variant1",
        variants=["variant1", "variant2"],
    )


@pytest.mark.local
def test_create_feature_variant(setup):
    repo = setup
    repo.create_resource(feature_variant)
    assert repo.get_feature_variant("feature", "variant1") == feature_variant


@pytest.mark.local
def test_get_features(setup):
    repo = setup
    repo.create_resource(feature_variant)
    feature_variant2 = replace(feature_variant, variant="variant2")
    repo.create_resource(feature_variant2)

    features = repo.get_features()
    assert len(features) == 1
    assert features[0] == Feature(
        name="feature",
        default_variant="variant1",
        variants=["variant1", "variant2"],
    )


@pytest.mark.local
def test_create_training_set_variant(setup):
    repo = setup
    repo.create_resource(label_variant)
    repo.create_resource(feature_variant)
    repo.create_resource(training_set_variant)
    assert (
        repo.get_training_set_variant("training_set", "variant1")
        == training_set_variant
    )


@pytest.mark.local
def test_get_training_sets(setup):
    repo = setup
    repo.create_resource(label_variant)
    repo.create_resource(feature_variant)
    repo.create_resource(training_set_variant)
    training_set_variant2 = replace(training_set_variant, variant="variant2")
    repo.create_resource(training_set_variant2)

    training_sets = repo.get_training_sets()
    assert len(training_sets) == 1
    assert training_sets[0] == TrainingSet(
        name="training_set",
        default_variant="variant1",
        variants=["variant1", "variant2"],
    )


@pytest.mark.local
def test_create_user(setup):
    repo: MetadataRepository = setup
    repo.create_resource(test_user)
    retrieved_user = repo.get_user(test_user.name)
    assert retrieved_user == test_user


@pytest.mark.local
def test_get_users(setup):
    repo: MetadataRepository = setup

    user1 = test_user
    user2 = replace(test_user, name="test_user2")
    user3 = replace(test_user, name="test_user3")

    users = [user1, user2, user3]

    for user in users:
        repo.create_resource(user)

    retrieved_users = repo.get_users()
    assert len(retrieved_users) == 3
    assert retrieved_users == users
